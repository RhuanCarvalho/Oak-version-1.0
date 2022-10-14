import MetaTrader5 as mt5, pandas as pd, talib as ta


class Create_Candles_DataBase:

    def __init__(self):
        pass
        

    def init_conection_mt5(self):
        
        # Iniciando Conexão com MetaTrader5
        if not mt5.initialize():
            print("Erro ao conectar : ", mt5.last_error())
            quit()
        else:
            print("coneceted mt5!")


    def add_indicators(self, candles):
        df = pd.DataFrame()
        upper, middle, lower = [],[],[]
        
        df['media9'] = round(ta.SMA(candles.close, timeperiod=9))
        df['media20'] = round(ta.SMA(candles.close, timeperiod=20))
        df['media50'] = round(ta.SMA(candles.close, timeperiod=50))
        df['media200'] = round(ta.SMA(candles.close, timeperiod=200))
        upper, middle, lower = ta.BBANDS(candles.close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        df['upperBB'], df['middleBB'], df['lowerBB'] = round(upper), round(middle), round(lower)

        return df

    def get_candles_in_mt5_SaveInPathDatabase(self, ativo, period=mt5.TIMEFRAME_M2):


        # SALVAR POR ARQUIVO BRUTO
        #-----------------------------------------------------------------------------------------------------------------------------

        # Iniciando Conexão com MetaTrader5
        self.init_conection_mt5()

        # calcular quantidade de candles de 1 ano para teste IA
        candles_in_hour = int((60/period))   # quantidade de candles dentro de uma hora de acordo com o periodo fornecido
        hour = int(9)                        # o ativo WIN@ fica aberto aproximada 9horas por dia
        day_in_month = int(22)               # dias ativos dentro do mês 
        month_in_year = int(12)              # meses dentro do ano
        years = 0.3 #int(1)                       # (EDITAVEL) caso queira aumentar a quantidade de anos do arquivo bruto

        number_candles = int(hour * candles_in_hour * day_in_month * month_in_year * years)
        # print(number_candles)

        # função que retorna candles solicitados
        rates = mt5.copy_rates_from_pos(ativo, period, 0, number_candles)

        # salvando o retorno dos candles como DATAFRAME(pandas)
        candles = pd.DataFrame(rates)

        candles['volume'] = candles['real_volume']

        # Retirando colunas que não serão usadas
        candles = candles.drop(columns=["tick_volume","spread","real_volume"])

        # ajustando datetime para date
        candles["time"] = pd.to_datetime(candles["time"], unit='s')

        # adicionando media movel de 20 periodo ao DataFrame
        candles = candles.merge(
        self.add_indicators(candles),
        right_index=True, 
        left_index=True, 
        how='outer')

        aleat = candles[candles['media200'].isnull()]
        lastDatainNull = str(aleat.time.iloc[-1])[0:10]

        countIndex = 0
        for i in range(len(candles)):
            dataRemove = str(candles.time.iloc[i])[0:10]
            if dataRemove <= lastDatainNull:
                countIndex+=1

        candles = candles[countIndex:]
        

        # caminho e nome arquivo
        name_file = "File_OneYear_TIMEFRAME_{}.csv".format(period)
        path_file = "../Database/Arquivo_Bruto/{}".format(name_file)

        # # salvando arquivo bruto
        candles.to_csv(path_file, index=False)



        # SALVAR POR ARQUIVOS SEPARADOS
        #------------------------------------------------------------------------------------------------------------------------------
    

        # caminho e nome arquivo
        name_file = "File_OneYear_TIMEFRAME_{}.csv".format(period)
        path_file = "../Database/Arquivo_Bruto/{}".format(name_file)
    
        candles  = pd.read_csv(path_file)

        
        # variaveis para o for a seguir
        id_inicial = 0
        count_saves = 0

        # salvar separados por data(dia) e por numeração para leitura IA
        for i in range(len(candles)-1):
            
            date_0 = "{}".format(candles["time"].iloc[i])[0:10]
            date_1 = "{}".format(candles["time"].iloc[i+1])[0:10]

            if date_0 != date_1:
                print('\n') 
                print("{} - {}".format(date_0,date_1))

                # salvando em uma variavel DATAFRAME o tamnho separados por datas
                candles_modified = candles[ (id_inicial) : i+1 ]

                # modificando id_incial para que ele pegue  ultima posição
                id_inicial = i+1

                # salvando CSV por DATA(dia)
                name_file = "{}.csv".format(date_0)
                path_file = "../Database/Arquivos_Por_Data/{}".format(name_file)
                candles_modified.to_csv(path_file, index=False)
                print('{} Salvo com sucesso!'.format(name_file))

                # salvando CSV por Numero para leitura IA
                name_file = "{}.csv".format(count_saves)
                path_file = "../Database/Arquivos_Por_Numero_Read_IA/{}".format(name_file)
                candles_modified.to_csv(path_file, index=False)
                print('{} Salvo com sucesso!'.format(name_file))

                count_saves += 1
        print('\n\n')



if __name__ == '__main__':
    
    # Apenas para tratamento de dados
    # ---------------------------------------------------
    ativo = "WIN@"

    candles = Create_Candles_DataBase()
    candles.get_candles_in_mt5_SaveInPathDatabase(ativo)
    # ---------------------------------------------------

    
