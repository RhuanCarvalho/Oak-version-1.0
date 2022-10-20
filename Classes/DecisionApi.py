
from datetime import datetime
from Classes.Auxiliar import (
create_model_candles,
inputs_IA
) 
from Telegram.Telegram import Send_Telegram as msg
import os
import neat, pickle


class BetterWinner:

    def __init__(self, numero_generation):

        self.better = self.init_better(numero_generation)


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

        return neat.nn.FeedForwardNetwork.create(winner, config)



    def decision_the_better(self, candles):

        hora = datetime.now()
        
        candles = create_model_candles(candles)

        inputs_Better = inputs_IA(candles, 85)

        output = self.better.activate(inputs_Better)

        decision = output.index(max(output))

        # Buy para -> 0 
        if (decision == 0):
            print(f'Compra | {hora}')
            msg().send_message(3, f'API - Compra | {hora}')
            return 1

        # Sell para -> 1 
        if (decision == 1):
            print(f'Venda | {hora}')
            msg().send_message(3,f'API - Venda | {hora}')
            return -1

