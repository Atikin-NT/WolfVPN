import requests
import json

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
        r = self.session.post(url=self.login_url, json=payload)
        return r.status_code

    def _create_request(self, url:str, params: dict, type: str) -> (requests.Response, str):
        """делает GET или POST запрос сопределенными параметрами

        Args:
            url (str): url адрес
            params (dict): параметры
            type (str): тип запроса: GET или POST

        Returns:
            any: Возращает пару: requests.Response и exeption. Если ошибки не было, то exeption = None,
            иначе - str (сообщение об ошибке)
        """
        result = requests.Response()
        exeption = None
        current_request = {
            'GET': lambda url, params: self.session.get(url, params=params),
            'POST': lambda url, params: self.session.post(url, json=params),
        }
        try:
            r = current_request[type](url, params)
            
            if 'redirect' in r.url:
                status_code = self._login()
                assert status_code == 200

                r = current_request[type](url, params)
                assert r.status_code == 200

            result = r
            
        except requests.exceptions.InvalidURL:
            exeption = f'Invalid URL: {url}'
        except Exception as ex:
            exeption = f'Unknown error = {ex}'
        return result, exeption

    def get(self, url: str, params: dict) -> (requests.Response, str):
        """осуществляет GET запрос с параметрами

        Args:
            url (str): url адрес 
            params (params): параметры 

        Returns:
            _type_: (ответ сервера, ссобщение об ошибке или None)
        """
        return self._create_request(url, params, 'GET')

    def post(self, url: str, params: dict) -> (requests.Response, str):
        """осуществляет POST запрос с параметрами

        Args:
            url (str): url адрес 
            params (params): параметры 

        Returns:
            _type_: (ответ сервера, ссобщение об ошибке или None)
        """
        return self._create_request(url, params, 'POST')
