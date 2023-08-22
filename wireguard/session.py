import requests

class Request:
    """
    Отвечает за огранизацию работы модуля session. Если какие данные cokkie устарели,
    то этот класс их обновит.
    """
    def __init__(self, password: str, username: str, login_url: str) -> None:
        self.session = requests.Session()
        self.password = password
        self.username = username
        self.login_url = login_url

    def _login(self) -> int:
        """
        При необходимости обновляет куки в объекте сессии

        Returns:
            int: код ответа с запроса
        """
        payload = {
            'password': self.password,
            'username': self.username,
        }
        r = self.session.post(self.login_url, json=payload)
        return r.status_code

    def _create_request(self, url:str, params: dict, type: str) -> any:
        """делает GET или POST запрос сопределенными параметрами

        Args:
            url (str): url адрес
            params (dict): параметры
            type (str): тип запроса: GET или POST

        Returns:
            any: В случае успеха будет возращен либо JSON объект либо True. В случае ошибки будет False
        """
        result = False
        current_request = {
            'GET': lambda url, params: self.session.get(url, params=params),
            'POST': lambda url, params: self.session.post(url, json=params),
        }
        try:
            r = current_request[type](url, params)
            
            if r.text != 'true':
                status_code = self._login()
                assert status_code == 200

                r = current_request[type](url, params)
                assert r.status_code == 200

                result = r.json() if type == 'GET' else True
            
        except requests.exceptions.InvalidURL:
            print("Invalid URL", url)
        except Exception as ex:
            print("Unknown error = ", ex)

        return result

    def get(self, url: str, params: dict):
        return self._create_request(url, params, 'GET')

    def post(self, url: str, params: dict):
        return self._create_request(url, params, 'POST')
