import pandas as pd
from datetime import datetime
from Classes.Auxiliar   import (
calculete_size_gain_stop, 
calculete_valor_finaceiro_trade
)

class Pessoa:

    
    def __init__(self):

        self.stop_max                       = 250 # 250 maximo de stop
        self.valor_max_trade                = (51,-51)

        self.total_gain         = 0
        self.total_stop         = 0
        self.diario_gain        = 0
        self.diario_stop        = 0
        self.trades              = []

        self.marge_stop     = 5
        self.num_contratos  = 1

        self.size_Gain, self.size_Stop, self.stop, self.gain = 0,0,0,0

        self.candles = []
        self.candle_decision = []
   
    
    def buy(self, candle_decision, candles):
        
        self.candles = pd.DataFrame(candles).reset_index(drop=True)
        self.candle_decision = candle_decision
        self.type_order = 'BUY'
        self.size_Gain, self.size_Stop, self.stop, self.gain = calculete_size_gain_stop(self.candle_decision, self.type_order, self.marge_stop, self.stop_max)

        for i in range(len(self.candles)):

            # Retorno Valor Stop
            if (self.candles.low[i] <= self.stop):
                self.atualizar_vars('stop', i, self.stop)
                break
                
            # Retorno Valor Gain    
            if (self.candles.high[i] >= self.gain):
                self.atualizar_vars('gain', i, self.gain)
                break

    def sell(self, candle_decision, candles):

        self.candles = pd.DataFrame(candles).reset_index(drop=True)
        self.candle_decision = candle_decision
        self.type_order = 'SELL'
        self.size_Gain, self.size_Stop, self.stop, self.gain = calculete_size_gain_stop(self.candle_decision, self.type_order, self.marge_stop, self.stop_max)

        for i in range(len(self.candles)):

            # Retorno Valor Stop
            if (self.candles.high[i] >= self.stop):
                self.atualizar_vars('stop', i, self.stop)
                break

            # Retorno Valor Gain    
            if (self.candles.low[i] <= self.gain):
                self.atualizar_vars('gain', i, self.gain)
                break

    def atualizar_vars(self, stop_or_gain, index, saida):

        if stop_or_gain == 'stop':
            self.resultado = calculete_valor_finaceiro_trade(self.size_Stop, stop_or_gain, self.num_contratos, self.valor_max_trade)
            self.total_stop += 1
            self.diario_stop += 1
            self.trades.append({
                "tipo_trade": self.type_order,
                "data_trade_entrada": datetime.strptime(self.candle_decision.time, "%Y-%m-%d %H:%M:%S").timestamp(),
                "data_trade_saida": datetime.strptime(self.candles.time[index], "%Y-%m-%d %H:%M:%S").timestamp(),
                "trade_entrada": self.candle_decision.close,
                "trade_saida": saida,
                "stop": self.stop,
                "gain": self.gain,
                "resultado_valor": self.resultado,
                "resultado_pontos": self.size_Stop
            })
        

        if stop_or_gain == 'gain':
            self.resultado = calculete_valor_finaceiro_trade(self.size_Gain, stop_or_gain, self.num_contratos, self.valor_max_trade)
            self.total_gain += 1
            self.diario_gain += 1
            self.trades.append({
                "tipo_trade": self.type_order,
                "data_trade_entrada": datetime.strptime(self.candle_decision.time, "%Y-%m-%d %H:%M:%S").timestamp(),
                "data_trade_saida": datetime.strptime(self.candles.time[index], "%Y-%m-%d %H:%M:%S").timestamp(),
                "trade_entrada": self.candle_decision.close,
                "trade_saida": saida,
                "stop": self.stop,
                "gain": self.gain,
                "resultado_valor": self.resultado,
                "resultado_pontos": self.size_Gain
            })

