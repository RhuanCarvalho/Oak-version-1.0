import pandas as pd
from datetime import datetime
from Classes.Auxiliar   import (
calculete_size_gain_stop, 
calculete_valor_finaceiro_trade
)

class Pessoa:

    
    def __init__(self):

        self.total_gain         = 0
        self.total_stop         = 0
        self.diario_gain        = 0
        self.diario_stop        = 0
        self.trades              = []
   
    
    def add_trade(self, stop_or_gain, trade_dict):
        '''
            Recebe:
            - string: 'stop' or 'gain'
            - dict: dict de trade BUY or SELL
        '''
        if stop_or_gain == 'stop':
            self.total_stop += 1
            self.diario_stop += 1
        if stop_or_gain == 'gain':            
            self.total_gain += 1
            self.diario_gain += 1

        self.trades.append(trade_dict)


        

# -----------------------------------------
# Variaveis Globais
# -----------------------------------------
stop_max           = 250 # 250 maximo de stop
valor_max_trade    = (51,-51)
marge_stop         = 5
num_contratos      = 1
# -----------------------------------------

def buy_dict(candle_decision, candles):
    '''
        Retorna tupla():
        - string -> 'stop' or 'gain'
        - dict trade the BUY
        
    '''
    candles = pd.DataFrame(candles).reset_index(drop=True)
    type_order = 'BUY'
    size_Gain, size_Stop, stop, gain = calculete_size_gain_stop(candle_decision, type_order, marge_stop, stop_max)

    for i in range(len(candles)):

        # Retorno Valor Stop
        if (candles.low[i] <= stop):

            buy_trade = create_dict(
                stop_or_gain= 'stop', 
                entrada= candle_decision.close, 
                saida= stop,
                stop= stop,
                gain= gain,
                size_Stop=size_Stop,
                size_Gain=size_Gain,
                num_contratos=num_contratos,
                valor_max_trade=valor_max_trade,
                type_order=type_order,
                time_entrada=candle_decision.time, 
                time_saida=candles.time[i]
                )
            return ('stop', buy_trade)
            
        # Retorno Valor Gain    
        if (candles.high[i] >= gain):

            buy_trade = create_dict(
                stop_or_gain= 'gain', 
                entrada= candle_decision.close, 
                saida= gain,
                stop= stop,
                gain= gain,
                size_Stop=size_Stop,
                size_Gain=size_Gain,
                num_contratos=num_contratos,
                valor_max_trade=valor_max_trade,
                type_order=type_order,
                time_entrada=candle_decision.time, 
                time_saida=candles.time[i]
                )
            return ('gain', buy_trade)



def sell_dict(candle_decision, candles):
    '''
        Retorna tupla():
        - string -> 'stop' or 'gain'
        - dict trade the SELL
        
    '''
    candles = pd.DataFrame(candles).reset_index(drop=True)
    type_order = 'SELL'
    size_Gain, size_Stop, stop, gain = calculete_size_gain_stop(candle_decision, type_order, marge_stop, stop_max)

    for i in range(len(candles)):

        # Retorno Valor Stop
        if (candles.high[i] >= stop):

            sell_trade = create_dict(
                stop_or_gain= 'stop', 
                entrada= candle_decision.close, 
                saida= stop,
                stop= stop,
                gain= gain,
                size_Stop=size_Stop,
                size_Gain=size_Gain,
                num_contratos=num_contratos,
                valor_max_trade=valor_max_trade,
                type_order=type_order,
                time_entrada=candle_decision.time, 
                time_saida=candles.time[i]
                )
            return ('stop', sell_trade)

        # Retorno Valor Gain    
        if (candles.low[i] <= gain):

            sell_trade = create_dict(
                stop_or_gain= 'gain', 
                entrada= candle_decision.close, 
                saida= gain,
                stop= stop,
                gain= gain,
                size_Stop=size_Stop,
                size_Gain=size_Gain,
                num_contratos=num_contratos,
                valor_max_trade=valor_max_trade,
                type_order=type_order,
                time_entrada=candle_decision.time, 
                time_saida=candles.time[i]
                )
            return ('gain', sell_trade)

def create_dict(
    stop_or_gain, 
    entrada, # self.candle_decision.close
    saida,
    stop,
    gain,
    size_Stop,
    size_Gain,
    num_contratos,
    valor_max_trade,
    type_order,
    time_entrada, # self.candle_decision.time
    time_saida # self.candles.time[index]
    ):

    # 'stop' or 'gain'
    size_in_pontos = size_Stop if stop_or_gain == 'stop' else size_Gain

    resultado = calculete_valor_finaceiro_trade(size_in_pontos, stop_or_gain, num_contratos, valor_max_trade)
    
    return {
        "tipo_trade": type_order,
        "data_trade_entrada": datetime.strptime(time_entrada, "%Y-%m-%d %H:%M:%S").timestamp(),
        "data_trade_saida": datetime.strptime(time_saida, "%Y-%m-%d %H:%M:%S").timestamp(),
        "trade_entrada": entrada,
        "trade_saida": saida,
        "stop": stop,
        "gain": gain,
        "resultado_valor": resultado,
        "resultado_pontos": size_in_pontos
    }





# #================================================
# # MODELO ANTIGO DESSA CLASSE
# #================================================

# import pandas as pd
# from datetime import datetime
# from Classes.Auxiliar   import (
# calculete_size_gain_stop, 
# calculete_valor_finaceiro_trade
# )

# class Pessoa:

    
#     def __init__(self):

#         self.stop_max                       = 250 # 250 maximo de stop
#         self.valor_max_trade                = (51,-51)

#         self.total_gain         = 0
#         self.total_stop         = 0
#         self.diario_gain        = 0
#         self.diario_stop        = 0
#         self.trades              = []

#         self.marge_stop     = 5
#         self.num_contratos  = 1

#         self.size_Gain, self.size_Stop, self.stop, self.gain = 0,0,0,0

#         self.candles = []
#         self.candle_decision = []
   
    
#     def buy(self, candle_decision, candles):
        
#         self.candles = pd.DataFrame(candles).reset_index(drop=True)
#         self.candle_decision = candle_decision
#         self.type_order = 'BUY'
#         self.size_Gain, self.size_Stop, self.stop, self.gain = calculete_size_gain_stop(self.candle_decision, self.type_order, self.marge_stop, self.stop_max)

#         for i in range(len(self.candles)):

#             # Retorno Valor Stop
#             if (self.candles.low[i] <= self.stop):
#                 self.atualizar_vars('stop', i, self.stop)
#                 break
                
#             # Retorno Valor Gain    
#             if (self.candles.high[i] >= self.gain):
#                 self.atualizar_vars('gain', i, self.gain)
#                 break

#     def sell(self, candle_decision, candles):

#         self.candles = pd.DataFrame(candles).reset_index(drop=True)
#         self.candle_decision = candle_decision
#         self.type_order = 'SELL'
#         self.size_Gain, self.size_Stop, self.stop, self.gain = calculete_size_gain_stop(self.candle_decision, self.type_order, self.marge_stop, self.stop_max)

#         for i in range(len(self.candles)):

#             # Retorno Valor Stop
#             if (self.candles.high[i] >= self.stop):
#                 self.atualizar_vars('stop', i, self.stop)
#                 break

#             # Retorno Valor Gain    
#             if (self.candles.low[i] <= self.gain):
#                 self.atualizar_vars('gain', i, self.gain)
#                 break

#     def atualizar_vars(self, stop_or_gain, index, saida):

#         if stop_or_gain == 'stop':
#             self.resultado = calculete_valor_finaceiro_trade(self.size_Stop, stop_or_gain, self.num_contratos, self.valor_max_trade)
#             self.total_stop += 1
#             self.diario_stop += 1
#             self.trades.append({
#                 "tipo_trade": self.type_order,
#                 "data_trade_entrada": datetime.strptime(self.candle_decision.time, "%Y-%m-%d %H:%M:%S").timestamp(),
#                 "data_trade_saida": datetime.strptime(self.candles.time[index], "%Y-%m-%d %H:%M:%S").timestamp(),
#                 "trade_entrada": self.candle_decision.close,
#                 "trade_saida": saida,
#                 "stop": self.stop,
#                 "gain": self.gain,
#                 "resultado_valor": self.resultado,
#                 "resultado_pontos": self.size_Stop
#             })
        

#         if stop_or_gain == 'gain':
#             self.resultado = calculete_valor_finaceiro_trade(self.size_Gain, stop_or_gain, self.num_contratos, self.valor_max_trade)
#             self.total_gain += 1
#             self.diario_gain += 1
#             self.trades.append({
#                 "tipo_trade": self.type_order,
#                 "data_trade_entrada": datetime.strptime(self.candle_decision.time, "%Y-%m-%d %H:%M:%S").timestamp(),
#                 "data_trade_saida": datetime.strptime(self.candles.time[index], "%Y-%m-%d %H:%M:%S").timestamp(),
#                 "trade_entrada": self.candle_decision.close,
#                 "trade_saida": saida,
#                 "stop": self.stop,
#                 "gain": self.gain,
#                 "resultado_valor": self.resultado,
#                 "resultado_pontos": self.size_Gain
#             })