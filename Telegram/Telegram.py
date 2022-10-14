# importar biblioteca para requisições http
import requests

class Send_Telegram:

    def __init__(self):
        self.token = '5520425373:AAGr1foiS8hspd5jBF6fl9sxkytLPhokqOk'
        
        self.habilitado = True

        self.chat_id = 0

        self.for_error  = -617430925
        self.for_log    = -776722336
        self.for_api    = -724247198
        
    # mostra o id do último grupo adicionado
    def last_chat_id(self):
        try:
            response = requests.get(f'https://api.telegram.org/bot{self.token}/getUpdates')
            if response.status_code == 200:
                json_msg = response.json()
                for json_result in reversed(json_msg['result']):
                    message_keys = json_result['message'].keys()
                    if ('new_chat_member' in message_keys) or ('group_chat_created' in message_keys):
                        return json_result['message']['chat']['id']
                print('Nenhum grupo encontrado')
            else:
                print('A resposta falhou, código de status: {}'.format(response.status_code))
        except Exception as e:
            print("Erro no getUpdates:", e)

    def group_selected(self, select_group):

        if select_group == 1:
            self.chat_id = self.for_error
        if select_group == 2:
            self.chat_id = self.for_log 
        if select_group == 3:
            self.chat_id = self.for_api

    # enviar mensagens utilizando o bot para um chat específico
    def send_message(self, select_group, message):
        '''
        select_group : 
        - 1 : Error in Code
        - 2 : Log Generation NEAT
        - 3 : Log API Oak
        '''

        self.group_selected(select_group)

        if self.habilitado:
            try:
                data = {"chat_id": self.chat_id, "text": message}
                url = f"https://api.telegram.org/bot{self.token}/sendMessage"
                requests.post(url, data)
            except Exception as e:
                print("Erro no sendMessage:", e)
        else:
            print('Telegram Desabilitado')

    def send_file(self,select_group, file):

        '''
        select_group : 
        - 1 : Error in Code
        - 2 : Log Generation NEAT
        - 3 : Log API Oak
        '''

        self.group_selected(select_group)
        
        if self.habilitado:
            try:
                data = {"chat_id": self.chat_id}
                files = {"document":open(file, 'rb')}
                url = f"https://api.telegram.org/bot{self.token}/sendDocument"
                requests.post(url, data, files=files)
            except Exception as e:
                print("Erro no sendMessage:", e)
        else:
            print('Telegram Desabilitado')



if __name__ == '__main__':
    
    # Pegar o codigo do ultimo grupo em que o bot foi add
    print(Send_Telegram().last_chat_id())

    Send_Telegram().send_message(3,'Vamos Ficar Ricos!')
 
    Send_Telegram().send_file(1, 'log.txt')
