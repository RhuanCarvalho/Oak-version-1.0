import sys, numpy as np, time
from concurrent.futures.process import ProcessPoolExecutor as exe
from multiprocessing import cpu_count
from Classes.Decorators         import calcule_time_function

from Classes.Custom_NEAT        import Custom_NEAT
from Classes.Pessoas            import buy_dict, sell_dict
from Classes.Sub_Training       import Sub_Training
from Classes.Auxiliar           import (
verify_hourInit_hourEnd,
inputs_IA,
load_RuleColor,
calcule_porcent
)


def calcule_inputs(input_IA, rede):
    return rede.activate(input_IA)

class Training(Sub_Training):
    
    def __init__(self):
    
        Sub_Training.__init__(self)
        self.custom_neat    = Custom_NEAT()


    @calcule_time_function
    def fitness_function_Oak(self, genomas_originais, config):
        
        # Criar dias para Treinamento
        print('Crindo Dias!\n')
        self.create_days()

        # lista para variaveis necessarias para IA (Todos os indices serão iguais e correspondentes)
        print('Resetando listas!\n')
        self.reset_list()

        # self.dias_testados = 0

        # estruturando variaveis para IA Treinar
        print('Iniciando Varias Genomas e Redes!\n')
        self.init_var_fitness_function(genomas_originais, config)

        print('Create Multi Process!\n')
        if __name__ == 'Classes.Training':
            with exe(max_workers=cpu_count()) as executor:

                print('Run training!\n')
                while True:

                    # Verificação Total Candles Treinamento
                    self.atualizar_candles()
                    
                    # Iniciar history / ESPECIFICO CAPITAL DIARIO
                    self.reset_vars_intra_day()
                    
                    # Encerrar Train
                    if (self.finalize):
                        self.finalize = False
                        break

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
                            if (load_RuleColor(self.candles[range_RuleColor_init:range_RuleColor_end], self.min_size_candle)):
                                time_candle = self.candles.time[range_RuleColor_end]

                                # criando inputs de trades
                                buy_sl_or_gn, buy_trade_dict, validade_trade = buy_dict(self.candles.iloc[range_RuleColor_end - 1], self.candles.iloc[range_RuleColor_end:]) 
                                sell_sl_or_gn, sell_trade_dict, validade_trade = sell_dict(self.candles.iloc[range_RuleColor_end - 1], self.candles.iloc[range_RuleColor_end:]) 

                                if validade_trade:

                                    # criando inputs para IA de acordo com o padrão
                                    input_IA = np.array(inputs_IA(self.candles[range_InputsIA_init:range_InputsIA_end], self.min_size_candle), dtype=np.int32)
                                    inputs = np.array([ input_IA for i in range(self.size_populacao)])

                                    start_time = time.time()
                                    outputs = [ out for out in executor.map(calcule_inputs, inputs, self.redes) ]
                                    end_time = time.time()

                                    # percorrer pessoas (o que cada pessoas criada pela IA vai tomar de decis�o)
                                    for i, pessoa in enumerate(self.pessoas):
                        
                                        # passando entradas para IA para obter output
                                        # output = self.redes[i].activate(input_IA)    
                                        # action = output.index(max(output))
                                        action = outputs[i].index(max(outputs[i]))

                                        # Tomadas de Decisão   BUY / SELL / NOT_ACTION
                                        if action == 0: # BUY
                                            pessoa.add_trade(buy_sl_or_gn, buy_trade_dict)
                                                                            
                                        if action == 1: #  SELL 
                                            pessoa.add_trade(sell_sl_or_gn, sell_trade_dict)                               

                                    sys.stdout.write(f'\rDate: {time_candle} [Run Pop: {round(end_time-start_time,2):<5}s]| Total dias: {self.total_candles_para_treinamento} | Total Dias Percorridos: { self.num_current_file}')

            
                    self.add_data_in_history_diario(self.candles.iloc[0].time[:10])

            # count Dias
            # self.dias_testados += 1

        self.score_fitness()

        self.send_api()

        # Encerrar e salvar melhor genomas
        if self.encerramento:
            self.finish_and_save()
        else:
            print('Training Finish Generation!\n')
            self.current_generation +=1   

        print('\n')

    def start(self, config_file):

        # Pegar população restaurada / ou inciado do 0
        populacao, self.current_generation = self.custom_neat.get_population(config_file)

        # Treinamento IA
        self.custom_neat.best = populacao.run(self.fitness_function_Oak) # , 1) -> caso precise para de rodar por determinado numero de gerações

        # salva o melhor genoma / pega o numero da geração atual para salvar no arquivo do melhor genoma
        self.custom_neat.save_best(self.current_generation)
        print(f"Melhor Genoma Salvo - Generation : {self.current_generation}")
