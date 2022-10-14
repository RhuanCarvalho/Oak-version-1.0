import os, traceback
from Classes.Training import Training
from Telegram.Telegram import Send_Telegram as msg

if __name__ == '__main__':

# Iniciar Oak Train NEAT

    try:  
        # Pegar caminho das configurações de NEAT
        this_file = os.path.dirname(__file__)
        config_file = os.path.join(this_file, 'config.txt')

        Training().start(config_file)

    except Exception:

        message = f'''
            \nHouve o Seguinte erro na execução do Codigo: 
            \n--------------------------------------------------
            \n{traceback.format_exc()}
            \n--------------------------------------------------
            \nFazer verificação do codigo
        ''' 

        msg().send_message(1,message)
        print(message)