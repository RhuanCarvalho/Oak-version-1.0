import sys
from Classes.Decorators         import calcule_time_function

from Classes.Custom_NEAT        import Custom_NEAT
from Classes.Sub_Training       import Sub_Training
from Classes.Auxiliar           import (
verify_hourInit_hourEnd,
inputs_IA,
load_RuleColor
)


class Training(Sub_Training):
    
    def __init__(self):
    
        Sub_Training.__init__(self)
        self.custom_neat    = Custom_NEAT()
        
        # Criar dias para Treinamento
        self.create_days()

    @calcule_time_function
    def fitness_function_Oak(self, genomas_originais, config):

        # lista para variaveis necessarias para IA (Todos os indices serão iguais e correspondentes)
        self.reset_list()

        self.dias_testados = 0

        # estruturando variaveis para IA Treinar
        self.init_var_fitness_function(genomas_originais, config)

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

                        # criando inputs para IA de acordo com o padrão
                        input_IA = inputs_IA(self.candles[range_InputsIA_init:range_InputsIA_end], self.min_size_candle)

                        # percorrer pessoas (o que cada pessoas criada pela IA vai tomar de decis�o)
                        for i, pessoa in enumerate(self.pessoas):
                            
                            # passando entradas para IA para obter output
                            output = self.redes[i].activate(input_IA)    
                            action = output.index(max(output))

                            # Tomadas de Decisão   BUY / SELL / NOT_ACTION
                            if action == 0: # BUY
                                pessoa.buy(self.candles.iloc[range_RuleColor_end - 1], self.candles.iloc[range_RuleColor_end:])
                                                                
                            if action == 1: #  SELL 
                                pessoa.sell(self.candles.iloc[range_RuleColor_end - 1], self.candles.iloc[range_RuleColor_end:])                               

                sys.stdout.write(
                    f'\rDate: {self.candles.time[range_RuleColor_end]} | Total dias: {self.total_candles_para_treinamento} | Total Dias Percorridos: { self.dias_testados}'
                    )

            
            self.add_data_in_history_diario(self.candles.iloc[0].time[:10])

            # count Dias
            self.dias_testados += 1

        self.score_diario()

        self.send_api()

        # Encerrar e salvar melhor genomas
        if self.encerramento:
            self.finish_and_save()
        else:
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
