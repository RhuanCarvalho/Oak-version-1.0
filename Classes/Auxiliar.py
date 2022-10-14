import pandas as pd, talib as ta
from datetime import time

from statistics import median_high


def create_model_candles(candles_bruto):

    candles = pd.DataFrame(candles_bruto)
    candles["time"] = pd.to_datetime(candles["time"], unit='s')

    # print(candles)

    upper, middle, lower = [],[],[]
        
    candles['media9'] = round(ta.SMA(candles.close, timeperiod=9))
    candles['media20'] = round(ta.SMA(candles.close, timeperiod=20))
    candles['media50'] = round(ta.SMA(candles.close, timeperiod=50))
    candles['media200'] = round(ta.SMA(candles.close, timeperiod=200))
    upper, middle, lower = ta.BBANDS(candles.close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    candles['upperBB'], candles['middleBB'], candles['lowerBB'] = round(upper), round(middle), round(lower)

    return candles[-10:]

     
def calculete_valor_finaceiro_trade( size_in_pts, result, num_contratos, valor_max_trade):
    
    valor = size_in_pts * 0.20 * num_contratos 

    if (result == "stop"):
        valor = valor *(-1)
    if (result == "gain"):
        valor = valor
        
    if ((valor > valor_max_trade[0]) or (valor < valor_max_trade[1])):
        print('Esse valor Ultrapassou: R$ {valor} | Corrigir codigo')
    
    return valor

def calculete_size_gain_stop(candle_, order, marge_stop, stop_max):
    
    # candle negativo(-1) ou positivo(1)
    negOrPos = (1)if((candle_.close - candle_.open) >= 0)else(-1)
    
    if (order == 'BUY'):

        # candle Positivo
        if (negOrPos == 1):
            
            size_Stop = (candle_.close - candle_.low) + marge_stop
            size_Gain = candle_.close - candle_.low

        # canlde Negativo   
        if (negOrPos == -1):

            size_Stop = (candle_.high - candle_.close) + marge_stop
            size_Gain = candle_.high - candle_.close

        # Caso a pontuação seja maior que stop maximo
        if (size_Stop > stop_max):

            size_Stop = stop_max
            size_Gain = stop_max

        # preços para rerificação 
        stop = candle_.close - size_Stop
        gain = candle_.close + size_Gain



    if (order == 'SELL'):

        # candle Positivo
        if (negOrPos == 1):
        
            size_Stop = (candle_.close - candle_.low) + marge_stop
            size_Gain = candle_.close - candle_.low

        # canlde Negativo   
        if (negOrPos == -1):

            size_Stop = (candle_.high - candle_.close) + marge_stop
            size_Gain = candle_.high - candle_.close

        # Caso a pontuação seja maior que stop maximo
        if (size_Stop > stop_max):

            size_Stop = stop_max
            size_Gain = stop_max
        
        # preços para rerificação 
        stop = candle_.close + size_Stop
        gain = candle_.close - size_Gain    
        

    return size_Gain, size_Stop, stop, gain

def verify_hourInit_hourEnd( candle_verify,hourMinute_init, hourMinute_end):
    hour_candle = int(candle_verify.time[10:13])
    minute_candle = int(candle_verify.time[14:16])
    time_candle = time(hour=hour_candle,minute=minute_candle)

    if ( time_candle >= hourMinute_init and time_candle < hourMinute_end):
        return True
    else:
        return False

def calculete_body_for_RuleColor( candles):
    
    data = pd.DataFrame()

    body_size, body_size_plus = [], []

    for i in range(len(candles)):     

        body_size.append(abs(candles.open[i] - candles.close[i]))
        body_size_plus.append(abs(candles.low[i] - candles.high[i]))

    data['body_size'] = body_size
    data['body_size_plus'] = body_size_plus
    
    return data

def get_index(list_genomas, get_what_index):
    '''
    get_what_index:
    - 0 for just (better_indice)
    - 1 for ( better_indice, median_indice, bad_indice )
    '''

    # Add lista Fitness para array
    list_fitness = []
    for i in range(len(list_genomas)):
        list_fitness.append(list_genomas[i].fitness)

    better_indice = list_fitness.index(max(list_fitness))
    median_indice = list_fitness.index(median_high(list_fitness))
    bad_indice    = list_fitness.index(min(list_fitness))

    if ( get_what_index == 1 ):
        return better_indice, median_indice, bad_indice
    if ( get_what_index == 0 ):
        return better_indice

def calculete_point_in_box( candles, main_point):

    data = pd.DataFrame()
    open,high,low,close = [],[],[],[]

    for i in range(len(candles)):     
        open.append(int(candles.open[i] - main_point))
        high.append(int(candles.high[i] - main_point))
        low.append(int(candles.low[i] - main_point))
        close.append(int(candles.close[i] - main_point))

    data['open_point_inBox'] = open
    data['high_point_inBox'] = high
    data['low_point_inBox'] = low
    data['close_point_inBox'] = close

    return data

def calculete_porcentVolumeRefFirst(candles):

    data = pd.DataFrame()
    porcentVolumeRefFirst = []

    for i in range(len(candles)):
        if i == 0:     
            porcentVolumeRefFirst.append(100)
        else:
            porcentVolumeRefFirst.append(int((candles.volume[i]*100)/candles.volume[0]))

    data['PorcentVolumeRefFirst'] = porcentVolumeRefFirst
    
    # print(data)
    return data

def calculete_distance_CloseCandle_CloseBandasBollinger(candles, weight_porcent):
    data = pd.DataFrame()
    closeRelativeBandsUpper = []
    closeRelativeBandsLower = []
    closeRelativeBandsSizeDistance = []

    for i in range(len(candles)):
        value_porcent_BandsUpper = (candles.close[i] * 100 ) / candles.upperBB[i]
        closeRelativeBandsUpper.append(int(round(100-value_porcent_BandsUpper)*weight_porcent))                

        value_porcent_BandsLower = (candles.close[i] * 100 ) / candles.lowerBB[i]
        closeRelativeBandsLower.append(int(round(100-value_porcent_BandsLower)*weight_porcent))                

        sizeDistanceBands_porcent = (candles.upperBB[i] * 100 ) / candles.lowerBB[i]
        closeRelativeBandsSizeDistance.append(int(round(100-sizeDistanceBands_porcent)*weight_porcent))
        
    
    data['CloseRelativeBandsUpper'] = closeRelativeBandsUpper
    data['CloseRelativeBandsLower'] = closeRelativeBandsLower
    data['CloseRelativeBandsSizeDistance'] = closeRelativeBandsSizeDistance

    return data

def calculete_distance_CloseCandle_CloseMedias_9_20_50_200( candles, weight_porcent):
    data = pd.DataFrame()
    closeRelativeMedia9 = []
    closeRelativeMedia20 = []
    closeRelativeMedia50 = []
    closeRelativeMedia200 = []

    for i in range(len(candles)):
        value_porcent9 = (candles.close[i] * 100) / candles.media9[i]
        closeRelativeMedia9.append(int(round((100-value_porcent9)*weight_porcent)))

        value_porcent20 = (candles.close[i] * 100) / candles.media20[i]
        closeRelativeMedia20.append(int(round((100-value_porcent20)*weight_porcent)))

        value_porcent50 = (candles.close[i] * 100) / candles.media50[i]
        closeRelativeMedia50.append(int(round((100-value_porcent50)*weight_porcent)))

        value_porcent200 = (candles.close[i] * 100) / candles.media200[i]
        closeRelativeMedia200.append(int(round((100-value_porcent200)*weight_porcent)))

    data['CloseRelativeMedia9'] = closeRelativeMedia9
    data['CloseRelativeMedia20'] = closeRelativeMedia20
    data['CloseRelativeMedia50'] = closeRelativeMedia50
    data['CloseRelativeMedia200'] = closeRelativeMedia200

    return data

def calculete_paramsDefaultCandle(candles, min_size_candle, range_total):

    data = pd.DataFrame()
    
    size_total = []
    size_relative_size_min = []
    size_relative_range_total = []
    pos_or_neg = []
    pts_pavio_superior = []
    porcent_pavio_superior = []
    pts_Body = []
    porcent_Body = []
    pts_pavio_inferior = []
    porcent_pavio_inferior = []

    for i in range(len(candles)):

        # -- Passar padrão candle
        # tamanho total Candle (high -low)
        size_total.append(candles.high[i] - candles.low[i])

        #   - Cacular porecentagem candle em relação ao tamanho minimo
        size_relative_size_min.append(round(((size_total[i]) * 100) / min_size_candle)) 

        #   - Calcular porcentagem candle em relação ao tamanho range
        size_relative_range_total.append(round(((size_total[i]) * 100) / range_total)) 

        #  %PavioSup %Corpo %PavioInf - em relação ao tamanho do candled
        #   -   - Candle Positivo(1) ou Negativo(-1):
        pos_or_neg.append((1)if((candles.close[i] - candles.open[i]) >= 0)else(-1)) 

        #   -   - % Pavio Superior
        pts_pavio_superior.append((candles.high[i] - candles.close[i])if(pos_or_neg[i] == 1)else(candles.high[i] - candles.open[i])) 
        porcent_pavio_superior.append((round(((pts_pavio_superior[i])*100)/(size_total[i]))) if (pts_pavio_superior[i] != 0) else(0)) 

        #   -   - % Corpo Candle
        pts_Body.append(abs(candles.open[i] - candles.close[i])) 
        porcent_Body.append((round(((pts_Body[i])*100)/(size_total[i]))) if (pts_Body[i] != 0) else(0)) 

        #   -   - % Pavio Inferior
        pts_pavio_inferior.append((candles.open[i] - candles.low[i])if(pos_or_neg[i] == 1)else(candles.close[i] - candles.low[i])) 
        porcent_pavio_inferior.append((round(((pts_pavio_inferior[i])*100)/(size_total[i]))) if (pts_pavio_inferior[i] != 0) else(0)) 

    
    data['size_total']                =  size_total
    data['size_relative_size_min']    =  size_relative_size_min
    data['size_relative_range_total'] =  size_relative_range_total
    data['pos_or_neg']                =  pos_or_neg
    data['pts_pavio_superior']        =  pts_pavio_superior
    data['pts_Body']                  =  pts_Body
    data['pts_pavio_inferior']        =  pts_pavio_inferior
    data['porcent_pavio_superior']    =  porcent_pavio_superior
    data['porcent_Body']              =  porcent_Body
    data['porcent_pavio_inferior']    =  porcent_pavio_inferior

    return data

def create_inputs_IA(candles, *args):
    #-----------------------------------------------------------------------
    # Outros inputs passados pela função
    #   : 
    #   range_total
    #   range_positive
    #   range_negative
    #-----------------------------------------------------------------------
    inputs_ = list(args)
    #-----------------------------------------------------------------------
    #-----------------------------------------------------------------------
    
    for i in range(len(candles)):
        #-----------------------------------------------------------------------
        # Posição dentro do Range in Box
        #-----------------------------------------------------------------------
        inputs_.append(candles.open_point_inBox[i])
        inputs_.append(candles.high_point_inBox[i])
        inputs_.append(candles.low_point_inBox[i])
        inputs_.append(candles.close_point_inBox[i])
        #-----------------------------------------------------------------------

        #-----------------------------------------------------------------------
        # Porcetagem distancia de fechamento(closeCandle) em relação a CloseMedia(9,20,50,200), multiplicado pelo peso
        #-----------------------------------------------------------------------
        inputs_.append(candles.CloseRelativeMedia9[i])
        inputs_.append(candles.CloseRelativeMedia20[i])
        inputs_.append(candles.CloseRelativeMedia50[i])
        inputs_.append(candles.CloseRelativeMedia200[i])
        #-----------------------------------------------------------------------

        #-----------------------------------------------------------------------
        # Porcetagem distancia de fechamento(closeCandle) em relação a CloseBandsBollinger, multiplicado pelo peso
        #-----------------------------------------------------------------------
        inputs_.append(candles.CloseRelativeBandsUpper[i])
        inputs_.append(candles.CloseRelativeBandsLower[i])
        inputs_.append(candles.CloseRelativeBandsSizeDistance[i])
        #-----------------------------------------------------------------------

        #-----------------------------------------------------------------------
        # Porcetagem do Volume atual em referencia ao anterior
        #-----------------------------------------------------------------------
        inputs_.append(candles.PorcentVolumeRefFirst[i])
        #-----------------------------------------------------------------------


        #-----------------------------------------------------------------------
        # Parmetros referente ao candles:.values
        #   tamanho total do candle em pontos (high - low)
        #   Procentagem tamanho candle em relação ao tamanho minimo
        #   Procentagem tamanho candle em relação ao range do CAIXOTE
        #   
        #   Candle Postivo ou Negativo
        #   
        #   PavioSup/Corpo/PavioInf - em pts
        #   PavioSup/Corpo/PavioInf - em Porcentagem
        #   
        #-----------------------------------------------------------------------
        inputs_.append(candles.size_total[i])
        inputs_.append(candles.size_relative_size_min[i])
        inputs_.append(candles.size_relative_range_total[i])

        inputs_.append(candles.pos_or_neg[i])
        
        inputs_.append(candles.pts_pavio_superior[i])
        inputs_.append(candles.pts_Body[i])
        inputs_.append(candles.pts_pavio_inferior[i])
        
        inputs_.append(candles.porcent_pavio_superior[i])
        inputs_.append(candles.porcent_Body[i])
        inputs_.append(candles.porcent_pavio_inferior[i])
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------


    return tuple(inputs_)

def inputs_IA(candles, min_size_candle):

    candles = pd.DataFrame(candles).reset_index(drop=True)  
        
    # vars utils
    highMax_range   = candles.high.max()
    lowMin_range    = candles.low.min()
    main_point      = candles.open.iloc[-5]
    weight_porcent  = 100
    
    
    # Paramentros para IA
    #------------------------------------------------------
    # -- CAIXOTE:

    #   - Range_Total
    range_total     = int(highMax_range - lowMin_range)
    
    #   - Range Positivo (+) 
    range_positive  = int(highMax_range - main_point)
    
    #   - Range Negativo (-)
    range_negative  = int(lowMin_range - main_point)

    #   - Posição de cada dado (OHLC) do candle, considerando a abertura do candle three, o ultimo
    #   - adicionado a CANDLES as colunas:
    #   -   -:: open_point_inBox, high_point_inBox, low_point_inBox,close_point_inBox
    candles = candles.merge(
        calculete_point_in_box(candles, main_point),
        right_index=True, 
        left_index=True, 
        how='outer')
    
    # -- Calcular a distancia do CloseCandle em relação CloseMedia(9,20,50,200) de cada candle com Peso(weight_porcent) para melhor leitura IA
    #   - adicionado a CANDLES a coluna:
    #   -   -:: CloseRelativeMedia9
    #   -   -:: CloseRelativeMedia20
    #   -   -:: CloseRelativeMedia50
    #   -   -:: CloseRelativeMedia200
    candles = candles.merge(
        calculete_distance_CloseCandle_CloseMedias_9_20_50_200(candles, weight_porcent),
        right_index=True, 
        left_index=True, 
        how='outer')

    # -- Calcular a distancia do CloseCandle em relação CloseBandsBollinger de cada candle com Peso(weight_porcent) para melhor leitura IA
    #   - adicionado a CANDLES a coluna:
    #   -   -:: CloseRelativeBandsUpper
    #   -   -:: CloseRelativeBandsLower
    #   -   -:: CloseRelativeBandsSizeDistance
    candles = candles.merge(
        calculete_distance_CloseCandle_CloseBandasBollinger(candles, weight_porcent),
        right_index=True, 
        left_index=True, 
        how='outer')

    # # -- Passar padrão candle
    candles = candles.merge(
        calculete_paramsDefaultCandle(candles, min_size_candle, range_total),
        right_index=True, 
        left_index=True, 
        how='outer')

    # # -- Porcentagem Volume referente ao anterior
    candles = candles.merge(
        calculete_porcentVolumeRefFirst(candles),
        right_index=True, 
        left_index=True, 
        how='outer')

    
    return create_inputs_IA(candles, range_total, range_positive, range_negative)
