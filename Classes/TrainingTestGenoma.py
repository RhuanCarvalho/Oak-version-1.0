from Classes.Decorators         import calcule_time_function

from Classes.Sub_TestGenoma       import Sub_TestGenoma
from Classes.Pessoas            import buy_dict, sell_dict

from Classes.Auxiliar           import (
verify_hourInit_hourEnd
)


class TrainingTestGenoma(Sub_TestGenoma):
    
    def __init__(self):
    
        Sub_TestGenoma.__init__(self)

        # Criar dias para Treinamento
        self.create_days()

    @calcule_time_function
    def fitness_function_Oak(self):
        print('Iniciando Teste\n')

        self.select_day()

        # percorrer candles
        for j in range(self.percorrer_candles):

            # provavelmente essa logica dara erro se o primerio padrão Rule Color se encaixar
            # add entrada por horario
            range_RuleColor_init = j
            range_RuleColor_end = j + 4
            range_InputsIA_init = (j-6)
            range_InputsIA_end = (j-6) + 10

            # para que que o indice inicial em inputs IA não seja negativo
            if (range_InputsIA_init < 0):
                continue

            # Verificar horário de inicio e fim de cada dia 
            if(verify_hourInit_hourEnd(self.candles.iloc[range_RuleColor_end - 1], self.hourMinute_init, self.hourMinute_end)):

                # codigo de Buy or Sell só sera ativado se a regra de coloração for ativada
                if (self.load_RuleColor(self.candles[range_RuleColor_init:range_RuleColor_end])):

                    # criando inputs de trades
                    buy_sl_or_gn, buy_trade_dict, validade_trade = buy_dict(self.candles.iloc[range_RuleColor_end - 1], self.candles.iloc[range_RuleColor_end:]) 
                    sell_sl_or_gn, sell_trade_dict, validade_trade = sell_dict(self.candles.iloc[range_RuleColor_end - 1], self.candles.iloc[range_RuleColor_end:]) 

                    if validade_trade:
                        
                        # passando entradas para IA para obter output
                        action = self.decision_rede(self.candles[range_InputsIA_init:range_InputsIA_end], self.min_size_candle)

                        # Tomadas de Decisão   BUY / SELL / NOT_ACTION
                        if action == 0: # BUY
                            self.pessoa.add_trade(buy_sl_or_gn, buy_trade_dict)
                                                            
                        if action == 1: #  SELL 
                            self.pessoa.add_trade(sell_sl_or_gn, sell_trade_dict)                               

        
        self.add_data_in_history_diario(self.candles.iloc[0].time[:10])

        self.send_api()

        print('Fim Teste\n')

    def start(self):
        self.fitness_function_Oak()
