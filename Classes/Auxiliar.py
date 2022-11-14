import pandas as pd, talib as ta
from datetime import time
from numba import jit

from statistics import median_high

@jit(nopython=True, cache=True)
def calcule_porcent(valor_atual, valor_total):
    porcent_ = round((valor_atual*100)/(valor_total-1),2)
    return porcent_

def create_model_candles(candles_bruto):

    candles = pd.DataFrame(candles_bruto)
    candles["time"] = pd.to_datetime(candles["time"], unit='s')

    candles['volume'] = candles['real_volume']

    # Retirando colunas que não serão usadas
    candles = candles.drop(columns=["tick_volume","spread","real_volume"])

    upper, middle, lower = [],[],[]
        
    candles['media9'] = round(ta.SMA(candles.close, timeperiod=9))
    candles['media20'] = round(ta.SMA(candles.close, timeperiod=20))
    candles['media50'] = round(ta.SMA(candles.close, timeperiod=50))
    candles['media200'] = round(ta.SMA(candles.close, timeperiod=200))
    upper, middle, lower = ta.BBANDS(candles.close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    candles['upperBB'], candles['middleBB'], candles['lowerBB'] = round(upper), round(middle), round(lower)

    return candles[-10:]

def load_RuleColor(candles, min_size_candle):
    '''
        calcula a força do candle atual em relação ao três ultimos:
        - CANDLE FORTE: cujo corpo maior que o corpo dos 3 ultimos
        - CANDLE SUPER FORTE: cujo coropo maior que o tamanho da minima e maxima dos 3 ultimos

        Retorno Booleano (True or False)
    '''
    candles = pd.DataFrame(candles).reset_index(drop=True)  

    candles = pd.DataFrame(calculete_body_for_RuleColor(candles))

    
    # Todos candles fortes precisam ser maior que o candle minimo
    if  (candles.body_size.iloc[-1] > min_size_candle):
        # calcular CANDLE SUPER FORTE
        if(
            candles.body_size.iloc[-1] > candles.body_size_plus.iloc[-2] and
            candles.body_size.iloc[-1] > candles.body_size_plus.iloc[-3] and
            candles.body_size.iloc[-1] > candles.body_size_plus.iloc[-4] 
            ):
            return True
        # calcular CANDLE FORTE
        if(
            candles.body_size.iloc[-1] > candles.body_size.iloc[-2] and
            candles.body_size.iloc[-1] > candles.body_size.iloc[-3] and
            candles.body_size.iloc[-1] > candles.body_size.iloc[-4] 
            ):
            return True
    
    # Retorna False para caso não encaixe no padrão
    return False
     
@jit(nopython=True, cache=True)
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
        if (size_Stop >= stop_max):

            return 0,0,0,0, True

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
        if (size_Stop >= stop_max):

            return 0,0,0,0, True

            size_Stop = stop_max
            size_Gain = stop_max
        
        # preços para rerificação 
        stop = candle_.close + size_Stop
        gain = candle_.close - size_Gain    
        

    return size_Gain, size_Stop, stop, gain, False

def verify_hourInit_hourEnd( candle_verify, hourMinute_init, hourMinute_end):
    hour_candle = int(candle_verify.time[10:13])
    minute_candle = int(candle_verify.time[14:16])
    time_candle = time(hour=hour_candle,minute=minute_candle)

    if ( time_candle >= hourMinute_init and time_candle < hourMinute_end):
        return True
    else:
        return False


def verify_hourInit_hourEnd_real_Oak( candle_verify, hourMinute_init, hourMinute_end):
    hour_candle = int(candle_verify[10:13])
    minute_candle = int(candle_verify[14:16])
    time_candle = time(hour=hour_candle,minute=minute_candle)

    if ( time_candle >= hourMinute_init and time_candle < hourMinute_end):
        return True
    else:
        return False

def calculete_body_for_RuleColor(candles):
    
    data = pd.DataFrame()

    data['body_size'] = list(abs(o - c) for o, c in zip(candles.open, candles.close))
    data['body_size_plus'] = list(abs(l - h) for l, h in zip(candles.low,candles.high))
    
    return data

def get_index(list_genomas, get_what_index):
    '''
    get_what_index:
    - 0 for just (better_indice)
    - 1 for ( better_indice, median_indice, bad_indice )
    '''

    # Add lista Fitness para array
    list_fitness = list(ge.fitness for ge in list_genomas)

    better_indice = list_fitness.index(max(list_fitness))
    median_indice = list_fitness.index(median_high(list_fitness))
    bad_indice    = list_fitness.index(min(list_fitness))

    if ( get_what_index == 1 ):
        return better_indice, median_indice, bad_indice
    if ( get_what_index == 0 ):
        return better_indice

def calculete_point_in_box(candles, main_point):

    data = pd.DataFrame()

    data['open_point_inBox']  = list(int(o - main_point) for o in candles.open )
    data['high_point_inBox']  = list(int(h - main_point) for h in candles.high )
    data['low_point_inBox']   = list(int(l - main_point) for l in candles.low  )
    data['close_point_inBox'] = list(int(c - main_point) for c in candles.close)

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
    
    return data

def calculete_distance_CloseCandle_CloseBandasBollinger(candles, weight_porcent):
    data = pd.DataFrame()
    @jit(nopython=True, cache=True)
    def map_calcule(valor1, valor2):
        return int(round((100 - ((valor1*100)/valor2) ) * weight_porcent)) 

    data['CloseRelativeBandsUpper']         = list(map(map_calcule, candles.close, candles.upperBB)) 
    data['CloseRelativeBandsLower']         = list(map(map_calcule, candles.close, candles.lowerBB))
    data['CloseRelativeBandsSizeDistance']  = list(map(map_calcule, candles.upperBB, candles.lowerBB))

    return data

def calculete_distance_CloseCandle_CloseMedias_9_20_50_200(candles, weight_porcent):
    data = pd.DataFrame()
    @jit(nopython=True, cache=True)
    def map_calcule(valor1, valor2):
      return int(round((100 - ((valor1*100)/valor2) ) * weight_porcent)) 

    data['CloseRelativeMedia9']   = list(map(map_calcule, candles.close,candles.media9))
    data['CloseRelativeMedia20']  = list(map(map_calcule, candles.close,candles.media20))
    data['CloseRelativeMedia50']  = list(map(map_calcule, candles.close,candles.media50))
    data['CloseRelativeMedia200'] = list(map(map_calcule, candles.close,candles.media200))

    return data

def calculete_paramsDefaultCandle(candles, min_size_candle, range_total):

    data = pd.DataFrame()

    @jit(nopython=True, cache=True)
    def map_porcent_min_size_candle(valor):
        return int(round(((valor) * 100) / min_size_candle))

    @jit(nopython=True, cache=True)
    def map_porcent_range_total(valor):
        return int(round(((valor) * 100) / range_total))

    @jit(nopython=True, cache=True)
    def porcent_body_sup_inf(valor1, valor2):
        return (round(((valor1)*100)/(valor2))) if (valor1 != 0) else(0)
    
    # pts Pavio Superior
    @jit(nopython=True, cache=True)
    def pts_pavio_superior(open, close, high, pos_or_neg):
        return int((high - close)if(pos_or_neg == 1)else(high - open))

    # pts Corpo Candle
    @jit(nopython=True, cache=True)
    def pts_Body(open, close):
        return int(abs(open - close))

    # pts Pavio Inferior
    @jit(nopython=True, cache=True)
    def pts_pavio_inferior(open, close, low, pos_or_neg):
        return int((open - low)if(pos_or_neg == 1)else(close - low))


    # -- Passar padrão candle
        # tamanho total Candle (high -low)
    data['size_total']                =  list(int(high - low) for high, low in zip(candles.high, candles.low))

    #   - Cacular porecentagem candle em relação ao tamanho minimo
    data['size_relative_size_min']    =  list(map(map_porcent_min_size_candle, data['size_total']))

    #   - Calcular porcentagem candle em relação ao tamanho range
    data['size_relative_range_total'] =  list(map(map_porcent_range_total, data['size_total']))
    
    #  %PavioSup %Corpo %PavioInf - em relação ao tamanho do candled
    
        #   -   - Candle Positivo(1) ou Negativo(-1):
    data['pos_or_neg']                =  list((1)if (c - o)>=0 else(-1) for c, o in zip(candles.close, candles.open))

    #   -   - % Pts tamanho dos candles
    data['pts_pavio_superior']        =  list(map(pts_pavio_superior, candles.open, candles.close, candles.high, data['pos_or_neg']))
    data['pts_Body']                  =  list(map(pts_Body, candles.open, candles.close))
    data['pts_pavio_inferior']        =  list(map(pts_pavio_inferior, candles.open, candles.close, candles.low, data['pos_or_neg']))

    #   -   - % Porcentagem tamanho dos candles
    data['porcent_pavio_superior']    =  list(map(porcent_body_sup_inf, data['pts_pavio_superior'], data['size_total'] ))
    data['porcent_Body']              =  list(map(porcent_body_sup_inf, data['pts_Body'], data['size_total'] ))
    data['porcent_pavio_inferior']    =  list(map(porcent_body_sup_inf, data['pts_pavio_inferior'], data['size_total'] ))

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
