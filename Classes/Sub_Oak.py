import pprint
import sys 

import MetaTrader5 as mt5, pandas as pd, os, pickle, neat
from time import sleep
from datetime import time, datetime
from Telegram.Telegram import Send_Telegram as msg
from Classes.Sub_Training   import Sub_Training
from Classes.Auxiliar   import (
calculete_size_gain_stop,
create_model_candles,
inputs_IA,
load_RuleColor,
verify_hourInit_hourEnd_real_Oak
)

class Oak:

    def __init__(self):

        self.pp = pprint.PrettyPrinter(indent=4)

        self.sub =  Sub_Training()

        # passar numero da geração que foi salva
        id_generation = int(input("Digite o ID da Generation\n::::"))
        self.better = self.init_better_genoma(id_generation)

        self.min_size_candle = 85
        self.hourMinute_init    = time(hour=9,minute=18)  # horário de inicio 09:00
        self.hourMinute_end     = time(hour=14,minute=0) # horário de fim 12:00

        self.symbol   = str('WINZ22')
        self.stop_max = 265
        self.marge_stop  = 5
        self.qtd_contratos = float(1.0)

        self.fixe_date = '2022-10-24 09:02:00' # Data Aleatória apenas para inicializar var
    
    def init_better_genoma(self, numero_generation):

        # get file config
        this_file = os.path.dirname(__file__)
        config_file = os.path.join(this_file, '../config.txt')

        name_file = f'Saves/Saves_All_BetterGenomas_AllGenerations/BetterWinner generation - {numero_generation}.pkl'
        print(f'Usando arquivo: {name_file}\n')

        # Get Better Genoma Salvo
        with open(name_file, 'rb') as file:
            winner = pickle.load(file)
        
        # create config for neat
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_file
        )

        return neat.nn.FeedForwardNetwork.create(winner, config)

    def create_request(self, type_order, candle_decision):
        '''
        type_order: int 
            -> 0:Buy 
            -> 1:Sell
        '''

        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(self.symbol, "not found, can not call order_check()")

        if not symbol_info.visible:
            print(self.symbol, "is not visible, trying to switch on")
            if not mt5.symbol_select(self.symbol,True):
                print("symbol_select({}}) failed, exit",self.symbol)

        if type_order == 0:
            type_ = 'BUY'
            price_ = mt5.symbol_info_tick(self.symbol).ask # for Buy
            size_Gain, size_Stop, stop_price, gain_price, validade_trade = calculete_size_gain_stop(candle_decision, type_, self.marge_stop, self.stop_max)
            if validade_trade:
                msg().send_message(3, f'TRADE NÃO REALIZADO [ULTRAPASSOU STOP-MAX] | {str(candle_decision.time).replace(":", ".")}')
                return None
            else:
                msg().send_message(3, f'Oak - Compra | {str(candle_decision.time).replace(":", ".")}')
                take_ = price_ + size_Gain
                stop_ = price_ - size_Stop
                type_order_mt5 = mt5.ORDER_TYPE_BUY

        if type_order == 1:
            type_ = 'SELL'
            price_ = mt5.symbol_info_tick(self.symbol).bid # for Buy
            size_Gain, size_Stop, stop_price, gain_price, validade_trade = calculete_size_gain_stop(candle_decision, type_, self.marge_stop, self.stop_max)
            if validade_trade:
                msg().send_message(3, f'TRADE NÃO REALIZADO [ULTRAPASSOU STOP-MAX] | {str(candle_decision.time).replace(":", ".")}')
                return None
            else:
                msg().send_message(3, f'Oak - Venda | {str(candle_decision.time).replace(":", ".")}')
                take_ = price_ - size_Gain
                stop_ = price_ + size_Stop
                type_order_mt5 = mt5.ORDER_TYPE_SELL

        deviation = 1
        magic = 121523
        message = f'{type_} in symbol {self.symbol}'

        # create request
        request_order = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(self.qtd_contratos),
            "type": type_order_mt5,
            "price": float(price_),
            "sl": float(stop_),
            "tp": float(take_),
            "deviation": deviation,
            "magic": magic,
            "commemt": message,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN
        } 
        

        return request_order

    def verify_new_candle(self):

        print('\n')
        while True:
            candles = pd.DataFrame(
                mt5.copy_rates_from_pos(
                    self.symbol, mt5.TIMEFRAME_M2, 1, 2))
            candles['time'] = pd.to_datetime(candles['time'], unit='s')
            time_last_candle = str(candles['time'].iloc[-1])
            # print(candles)

            if self.fixe_date != time_last_candle:
                self.fixe_date = time_last_candle
                print(f'\nclose new candle : {time_last_candle}\n')
                break
            else:
                current_time = (datetime.now()).strftime('%H:%M:%S')
                sys.stdout.write(f'\rUltimo candle de verificação: {self.fixe_date} - time: {current_time}')
            sleep(0.01)

    def verify_rule_color(self):
        candles = pd.DataFrame(
                mt5.copy_rates_from_pos(
                    self.symbol, mt5.TIMEFRAME_M2, 1, 5))
        candles['time'] = pd.to_datetime(candles['time'], unit='s')
        # print(candles)   

        return load_RuleColor(candles, self.min_size_candle)

    def oak_send_order(self):
        '''
            Retorna:
                - 0 -> for Buy
                - 1 -> for Sell
        '''

        candles = create_model_candles(mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M2, 1, 220))
        inputs = inputs_IA(candles, self.min_size_candle)
        output = self.better.activate(inputs)
        decision = output.index(max(output))

        # #Salvar Candles para verificação
        # hour_ = str(candles.iloc[-1].time).replace(":", ".")
        # trade_ = 'BUY' if decision == 0 else 'SELL'
        # candles.to_csv(f'entradasOakReal/trade - {hour_} - {trade_}.csv', index=False)

        request_ = self.create_request(decision, candles.iloc[-1])
        if request_ == None:
            print('\nTrade Não Realizado - Stop Maior que Stop Max')
        else:
            result = mt5.order_check(request_)
            check_send_oreder = mt5.order_send(request_)
            
            print('\nRequest:\n')
            self.pp.pprint(request_)
            print('\nCheck:\n')
            self.pp.pprint(result)
            print('\nCheck Send Order:\n')
            self.pp.pprint(check_send_oreder)
            print('\n')

    def start(self):

        print('\n')
        while True:
            # aguarda sempre novo candle para prosseguir
            self.verify_new_candle()
            if (verify_hourInit_hourEnd_real_Oak(self.fixe_date, self.hourMinute_init, self.hourMinute_end)):
                if (self.verify_rule_color()):
                    self.oak_send_order()
            else:
                sys.stdout.write(f'\rFora do Horário de Negociação: {self.fixe_date}')
                


