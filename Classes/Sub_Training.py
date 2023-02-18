import sys
import neat, os, pandas as pd, requests
from time import sleep as t
from datetime import datetime, time


from Classes.Pessoas                        import Pessoa
from Classes.History                        import History
from Classes.Auxiliar                       import (
get_index,
calcule_porcent
)

class Sub_Training:

    def __init__(self):
        
        # Variaveis para Fitness Function

        self.url_generation = 'http://localhost:8080/generation'
        self.url_genoma = 'http://localhost:8080/genoma'
        self.url_training = 'http://localhost:8080/training'
        self.url_historytrades = 'http://localhost:8080/historytrade'
        self.url_dia = 'http://localhost:8080/dia'
        self.url_candles = 'http://localhost:8080/candles'

        self.finalize                       = False
        self.encerramento                   = False

        self.min_size_candle = 5
        self.current_generation             = 0 
        self.num_current_file               = 0
        self.dias_testados                  = 0
        self.total_candles_para_treinamento = 0
        self.num_candles_train              = 0 # treinar essa quantidade de dias
        self.percorrer_candles              = 0
        self.size_populacao                 = 0

        self.redes, self.genomas, self.pessoas, self.history = [],[],[],[]

        # porcentagem
        self.porcentMinGeral = 0
        self.porcentagem_desejada = 85
        self.porcentagem_media_atingida = []

        self.dias = []
        self.dias_para_enviar_api = []
        self.candles = []

        self.hourMinute_init    = time(hour=9,minute=18)  # horário de inicio 09:00
        self.hourMinute_end     = time(hour=14,minute=0) # horário de fim 12:00 

    def create_days(self):

        list_ = os.listdir('Database/Arquivos_Por_Numero_Read_IA')
        order_ = list([(int(i.replace('.csv','')), i) for i in list_ ])
        order_.sort()

        self.total_candles_para_treinamento = len(list_)
        self.num_candles_train = self.total_candles_para_treinamento - 1 # treinar essa quantidade de dias

        self.dias = list([pd.DataFrame(
            pd.read_csv(f'Database/Arquivos_Por_Numero_Read_IA/{name_file}')
                ) for i, name_file in order_])
        # self.dias.reverse()

    def reset_list(self):
        self.redes, self.genomas, self.pessoas, self.history = [],[],[],[]
        self.dias_para_enviar_api = []

    def init_var_fitness_function(self, genomas_originais, config):

        # estruturando variaveis para IA Treinar			
        size_populacao_genomas = len(genomas_originais)
        i=0
        for _, genoma in genomas_originais:
            sys.stdout.write(f'\rCreate Vars for FitnessFunction: {round(calcule_porcent(i,self.size_populacao),2):<5}%')
            i+=1

            # criando rede neural pessoa
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            
            # definindo fitness de cada genoma para come�ar em 0 		
            genoma.fitness = 0 	

            # add dados nas listas
            self.redes.append(rede)
            self.genomas.append(genoma)
            self.pessoas.append(Pessoa())
            self.history.append(History())

        self.size_populacao = len(self.pessoas)
        print(f'\nTamanho População Genomas: {size_populacao_genomas}')
        print(f'Tamanho População Pessoas: {self.size_populacao}\n')
            
    def atualizar_candles(self): 

        if open('encerramento.txt').read() == 'False':
            self.encerramento = False
        else:
            self.encerramento = True 

        if (self.num_current_file > self.num_candles_train):
            self.num_current_file = 0
            self.finalize = True
        else:
            self.candles = self.dias[self.num_current_file]
            # add index dos dias aqui
            self.dias_para_enviar_api.append(self.num_current_file)
            self.num_current_file += 1
            self.percorrer_candles = len(self.candles)-6
                
    def add_data_in_history_diario(self, data_diaria):

        for i in range(len(self.pessoas)):

            total_gain, total_loss = self.pessoas[i].diario_gain, self.pessoas[i].diario_stop

            total_value = sum([data["resultado_valor"] for data in self.pessoas[i].trades])

            total_trades = total_gain + total_loss
            porcent_gain = (round((total_gain * 100) / total_trades))
            porcent_loss = (round((total_loss * 100) / total_trades))

            self.history[i].history_dias.append({
                    "date": datetime.strptime(data_diaria, "%Y-%m-%d").timestamp(),
                    "resultado_diario_valor": total_value,
                    "total_trades_gain": total_gain,
                    "total_trades_loss": total_loss,
                    "total_trades": total_trades,
                    "porcent_trades_gain": porcent_gain, 
                    "porcent_trades_loss": porcent_loss,
                    "history_trades": self.pessoas[i].trades,
                })

    def score_fitness(self):
        print('\nAdd Score in Genomas :\n')
        self.porcentagem_media_atingida = []
        for i, hist in enumerate(self.history):
            sys.stdout.write(f'\rAdd Score Fitness in Genomes: {round(calcule_porcent(i,self.size_populacao),2):<5}%')

            porcent_dos_dias = [dia["porcent_trades_gain"] for dia in hist.history_dias]

            fitness_media_porcent_dias = sum(porcent_dos_dias)/len(porcent_dos_dias)
            self.porcentagem_media_atingida.append(fitness_media_porcent_dias)

            countMenorQue, count40, count50, count60, count70, count80, count90 = 0,0,0,0,0,0,0

            for porcent in porcent_dos_dias:
                if porcent < self.porcentMinGeral:
                    countMenorQue += 1
                if porcent >= 40:
                    count40 += 1
                if porcent >= 50:
                    count50 += 1
                if porcent >= 60:
                    count60 += 1
                if porcent >= 70:
                    count70 += 1
                if porcent >= 80:
                    count80 += 1
                if porcent >= 90:
                    count90 += 1

            if countMenorQue > 0:
                self.genomas[i].fitness += -1
            else:
                total_dias = len(porcent_dos_dias)

                porcent_dias_acima_40 = (count40*100)/total_dias
                porcent_dias_acima_50 = (count50*100)/total_dias
                porcent_dias_acima_60 = (count60*100)/total_dias
                porcent_dias_acima_70 = (count70*100)/total_dias
                porcent_dias_acima_80 = (count80*100)/total_dias
                porcent_dias_acima_90 = (count90*100)/total_dias

                fitness_porcent_dias =  porcent_dias_acima_40 + porcent_dias_acima_50 + porcent_dias_acima_60 + porcent_dias_acima_70 + porcent_dias_acima_80 + porcent_dias_acima_90 
                
                seqList1or1neg = []
                for varT in hist.history_dias:
                    for varD in varT['history_trades']:
                        seqList1or1neg.append(1 if varD['resultado_valor'] >= 0 else -1)

                seq_ = []
                count = 0

                for data in seqList1or1neg:
                    count += data
                    seq_.append(count)

                df = pd.DataFrame()
                df['seq_'] = seq_
                df['seq_without_drawdown'] = df['seq_'].cummax() 
                df['delta'] = df['seq_without_drawdown'] - df['seq_']

                totalPosivelDrawDown = (range(len(df.seq_)+1))[-1]
                totalDeltaDrawDown = df['seq_'].iloc[-1]

                fitness_TotalDeltaSemDrawDown = (totalDeltaDrawDown*100)/totalPosivelDrawDown

                maiorDrawDown = 100 - (df["delta"].max())
                fitness_MaiorDrawDown = 0 if maiorDrawDown < 0 else maiorDrawDown

                _fitness = fitness_media_porcent_dias + fitness_porcent_dias + fitness_TotalDeltaSemDrawDown + fitness_MaiorDrawDown

                self.genomas[i].fitness += _fitness

        print('\n')

    def reset_vars_intra_day(self):
        # Iniciar history / ESPECIFICO CAPITAL DIARIO
            for pessoa in self.pessoas:
                pessoa.trades = []
                pessoa.diario_stop = 0
                pessoa.diario_gain = 0 
    

    def send_api(self):
        try:
            self.send_data_api()
        except Exception as err:
            print(f'Houve o seguinte erro ao tentar fazer o envio dos dados para API: {err}')

    def send_data_api(self):

        print('\nEnviando Dias para Api:')
        #----------------------------------
        # Create Dias
        #----------------------------------
        for j in self.dias_para_enviar_api:
            dia = self.dias[j]
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
        # Create Generation
        #----------------------------------

        _generation = {
            "id_generation": self.current_generation,
            "total_dias_treinados": len(self.dias_para_enviar_api),
            "total_populacao": len(self.pessoas)
        }

        id_generation = (requests.post(self.url_generation, json=_generation)).json()
        t(0.0000002)


        # Passar apenas 10 melhores genomas para API
        list_10_melhores = []
        lista_fitness_e_index = []
        for i, gen in enumerate(self.genomas):
            lista_fitness_e_index.append((gen.fitness, i))
        lista_fitness_e_index.sort(reverse=True)
        list_10_melhores = lista_fitness_e_index[:10]

        print('\nEnviando 10 melhores Genomas para Api:')
        for _, i in list_10_melhores:

            totalValue = sum([result_days['resultado_diario_valor'] for result_days in self.history[i].history_dias])
            totalGains = sum([result_days['total_trades_gain'] for result_days in self.history[i].history_dias])
            totalLoss = sum([result_days['total_trades_loss'] for result_days in self.history[i].history_dias])
            totaltrades = sum([result_days['total_trades'] for result_days in self.history[i].history_dias])
            porcent_media_atingida = self.porcentagem_media_atingida[i]
            totalDiasTrain = len(self.history[i].history_dias)

            _genoma = {
                    "id_generation": id_generation,
                    "fitness": self.genomas[i].fitness,
                    "resultado_total_valor": totalValue,
                    "total_trades_gain": totalGains,
                    "total_trades_loss": totalLoss,
                    "total_trades": totaltrades,
                    "media_porcent_desejada": self.porcentagem_desejada,
                    "media_porcent_atingida": porcent_media_atingida,
                    "total_dias_training": totalDiasTrain,
                }
            
            id_genoma = (requests.post(self.url_genoma, json= _genoma)).json()
            t(0.0000002)

            for training in self.history[i].history_dias:
                training.update({"id_genoma": id_genoma})

                id_training = (requests.post(self.url_training, json=training)).json()
                t(0.0000002)

                for history in training['history_trades']:
                    history.update({"id_training":id_training})
                    id_historytrades = (requests.post(self.url_historytrades, json=history)).json()
        print('Enviado!')


    def finish_and_save(self):
        print('\nCriando Melhor Genoma!')
        #salvando o genoma com melhor pontuação
        self.genomas[get_index(self.genomas,0)].fitness = 1001
