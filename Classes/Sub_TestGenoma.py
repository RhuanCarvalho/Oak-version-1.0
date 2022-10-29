import pprint

import pickle
import neat, os, pandas as pd, requests
from time import sleep as t
from datetime import datetime, time


from Classes.Pessoas                        import Pessoa
from Classes.History                        import History
from Classes.Auxiliar                       import (
calculete_body_for_RuleColor,
inputs_IA
)

class Sub_TestGenoma:

    def __init__(self):

        self.pp = pprint.PrettyPrinter(indent=4)

        self.pessoa = Pessoa()
        self.history = History()

        id_generation = int(input("Digite o ID da Generation\n::::"))
        self.rede = self.init_better(id_generation)
        
        # Variaveis para Fitness Function
        self.url_training = 'http://localhost:8080/trainingoftest'
        self.url_historytrades = 'http://localhost:8080/historytradeoftest'
        self.url_dia = 'http://localhost:8080/dia'
        self.url_candles = 'http://localhost:8080/candles'

        self.finalize                       = False
        self.encerramento                   = False

        self.min_size_candle = 85
        self.current_generation             = 0 
        self.num_current_file               = 0
        self.dias_testados                  = 0
        self.total_candles_para_treinamento = len(os.listdir('Database/Arquivos_Por_Numero_Read_IA'))
        # self.num_candles_train              = 50 # treinar essa quantidade de dias
        self.num_candles_train              = self.total_candles_para_treinamento - 1 # treinar essa quantidade de dias
        self.percorrer_candles              = 0

        # porcentagem
        self.porcentMinGeral = 30
        self.porcentagem_desejada = 85
        self.porcentagem_media_atingida = []

        self.dias = []
        self.dias_para_enviar_api = []
        self.candles = []

        self.hourMinute_init    = time(hour=9,minute=18)  # horário de inicio 09:00
        self.hourMinute_end     = time(hour=14,minute=0) # horário de fim 12:00 

    def create_days(self):
        self.dias = list([pd.DataFrame(
            pd.read_csv(f'Database/Arquivos_Por_Numero_Read_IA/{str(i)}.csv')
                ) for i in range(self.total_candles_para_treinamento)])
        self.dias.reverse()
          
    def select_day(self): 
        for i, dia in enumerate(self.dias):
            print(f'ID: {i} - Arquivo: {dia.iloc[0].time[:10]}')

        select = int(input('Selecione um ID para selecionar o dia\n::::::'))
        
        self.candles = self.dias[select]
        # add index dos dias aqui
        self.num_current_file = select
        self.percorrer_candles = len(self.candles)-6
                
    def add_data_in_history_diario(self, data_diaria):

        total_gain, total_loss = self.pessoa.diario_gain, self.pessoa.diario_stop

        total_value = sum([data["resultado_valor"] for data in self.pessoa.trades])

        total_trades = total_gain + total_loss
        porcent_gain = (round((total_gain * 100) / total_trades))
        porcent_loss = (round((total_loss * 100) / total_trades))

        self.history.history_dias.append({
                "date": datetime.strptime(data_diaria, "%Y-%m-%d").timestamp(),
                "resultado_diario_valor": total_value,
                "total_trades_gain": total_gain,
                "total_trades_loss": total_loss,
                "total_trades": total_trades,
                "porcent_trades_gain": porcent_gain, 
                "porcent_trades_loss": porcent_loss,
                "history_trades": self.pessoa.trades,
            })
    
    def load_RuleColor(self, candles):
        '''
            calcula a força do candle atual em relação ao três ultimos:
            - CANDLE FORTE: cujo corpo maior que o corpo dos 3 ultimos
            - CANDLE SUPER FORTE: cujo coropo maior que o tamanho da minima e maxima dos 3 ultimos

            Retorno Booleano (True or False)
        '''
        candles = pd.DataFrame(candles).reset_index(drop=True)  

        candles = pd.DataFrame(calculete_body_for_RuleColor(candles))

        
        # Todos candles fortes precisam ser maior que o candle minimo
        if  (candles.body_size.iloc[-1] > self.min_size_candle):
            # calcular CANDLE SUPER FORTE
            if(
                candles.body_size.iloc[-1] > candles.body_size_plus.iloc[-2] and
                candles.body_size.iloc[-1] > candles.body_size_plus.iloc[-3] and
                candles.body_size.iloc[-1] > candles.body_size_plus.iloc[-4] 
                ):
                return True
            # calcular CANDLE FORTE
            if(
                candles.body_size.iloc[-1] > candles.body_size.iloc[-2] and
                candles.body_size.iloc[-1] > candles.body_size.iloc[-3] and
                candles.body_size.iloc[-1] > candles.body_size.iloc[-4] 
                ):
                return True
        
    
        # Retorna False para caso não encaixe no padrão
        return False

    def init_better(self, numero_generation):

        # get file config
        this_file = os.path.dirname(__file__)
        config_file = os.path.join(this_file, '../config.txt')

        name_file = f'Saves/Saves_Better_Winner/BetterWinner generation - {numero_generation}.pkl'
        print(f'Usando arquivo: {name_file}')

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

        rede = neat.nn.FeedForwardNetwork.create(winner, config)

        print('\n\nWinner Genoma\n\n')
        self.pp.pprint(vars(winner))
        print('\n\nRede Neural\n\n')
        self.pp.pprint(vars(rede))

        return rede

    def decision_rede(self, candles, min_size):

        inputs_Better = inputs_IA(candles, min_size)

        output = self.rede.activate(inputs_Better)

        decision = output.index(max(output))

        # #Salvar Candles para verificação
        # hour_ = str(candles.iloc[-1].time).replace(":", ".")
        # trade_ = 'BUY' if decision == 0 else 'SELL'
        # candles.to_csv(f'entradasOakTest/trade - {hour_} - {trade_}.csv', index=False)

        return decision

    def send_api(self):
        try:
            self.send_data_api()
        except Exception as err:
            print(f'Houve o seguinte erro ao tentar fazer o envio dos dados para API: {err}')

    def send_data_api(self):

        print('\nEnviando Dias para Api:')
        #----------------------------------
        # Create Dia
        #----------------------------------
        dia = self.dias[self.num_current_file]
        id_dia = (requests.post(self.url_dia, json={
            "dia": datetime.strptime(dia.time[0][:10], "%Y-%m-%d").timestamp()
            })).json()
        t(0.0000002)
        if id_dia != -1:
            for i in range(len(dia)):
                candle = {
                    "date": datetime.strptime(dia.time[i], "%Y-%m-%d %H:%M:%S").timestamp(),
                    "open": dia.open[i],
                    "high": dia.high[i],
                    "low": dia.low[i],
                    "close": dia.close[i],
                    "id_dia": id_dia
                }
                requests.post(self.url_candles,json=candle)
                t(0.0000002)
        print('Enviado!')

        #----------------------------------
        # Create Training Test
        #----------------------------------
        for training in self.history.history_dias:
            id_training = (requests.post(self.url_training, json=training)).json()
            t(0.0000002)

            for history in training['history_trades']:
                history.update({"id_training":id_training})
                id_historytrades = (requests.post(self.url_historytrades, json=history)).json()

       

