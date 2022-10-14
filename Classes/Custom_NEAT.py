import pickle, neat, os

class Custom_NEAT:

    def __init__(self):
        self.ultimo_arquivo = ''
        self.current_generation = 0

    def save_best(self, current_generation):
        # Realiza o Save do melhor genoma
        with open(f'Saves/Saves_Better_Winner/BetterWinner generation - {current_generation}.pkl', 'wb') as file:
            pickle.dump(self.best, file)

    def get_restore_checkpoint(self):
        
        # Pegar o ultimo checkpoint salvo
        caminho = 'Saves/Saves_Checkpoint'
        lista_arquivos = os.listdir(caminho)

        if(len(lista_arquivos) != 0):

            lista_datas = []
            for arquivo in lista_arquivos:
                data = os.path.getmtime(f'{caminho}/{arquivo}')
                lista_datas.append((data, arquivo))
            
            lista_datas.sort(reverse=True)

            # print(lista_datas)
            
            self.ultimo_arquivo = lista_datas[0][1]
            
            self.current_generation = int(self.ultimo_arquivo[16:])

            path_file = f'{caminho}/{self.ultimo_arquivo}'

            return neat.Checkpointer.restore_checkpoint(path_file)

        return None   



    def get_population(self, path_config_file):
        
        # Criar Configuração para passa como parametro para criar a população
        config = neat.config.Config(neat.DefaultGenome,
                                    neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet,
                                    neat.DefaultStagnation,
                                    path_config_file)

        # Se Usará algum ponto de restauração ou criará um nova do 0
        populacao = self.get_restore_checkpoint()
        if (populacao == None):
            print(f'IA iniciada a partir do ponto 0 - nenhum arquivo checkpoint encontrado')
            populacao = neat.Population(config)
        else:
            print(f'IA iniciada a partir do ponto de restauração do arquivo {self.ultimo_arquivo}')

        # Atualização de status IA
        populacao.add_reporter(neat.StdOutReporter(True))
        populacao.add_reporter(neat.StatisticsReporter())

        # neat.Checkpointer.save_checkpoint()
        populacao.add_reporter(neat.Checkpointer(1, 1, 'Saves/Saves_Checkpoint/neat-checkpoint-'))


        return populacao, self.current_generation





       