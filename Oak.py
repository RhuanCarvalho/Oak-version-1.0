import MetaTrader5 as mt5
from Classes.Sub_Oak import Oak


login    =int(83929175)
# login    =int(73929175)

password =str('Rc837105')
server   =str('XPMT5-DEMO')


if __name__ == '__main__':

    if not mt5.initialize(
        login=login,
        password=password,
        server=server
    ):
        print('Erro ao conectar: ', mt5.last_error())
        quit()
    else:
        print('\n!!!! Conectado com sucesso! !!!!\n')
        Oak().start()