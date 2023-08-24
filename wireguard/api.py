from .session import Request
from . import utils
import requests

class API:

    def __init__(self, password: str, username: str, login_url: str, main_url: str) -> None:
        self.request = Request(password, username, login_url)
        self.url = main_url

    def _is_json(self, r: requests.Response) -> any:
        try:
            res = r.json()
        except ValueError as e:
            return False
        return res

    def _available_ips(self, config_name: str) -> str:
        """получает список доступных ip адресов

        Args:
            config_name (str): название конфигурации

        Returns:
            dict: список ip
        """
        url = self.url + f'/available_ips/{config_name}'
        data, err = self.request.get(url, {})
        
        data_json = self._is_json(data)
        if err is None and data_json is not False:
            data = data_json[0] if len(data_json) != 0 else ''
        else:
            data = ''
        
        return data

    def get_config(self, config_name: str, search="") -> any:
        """получение всех конфигурации с сервера

        Args:
            config_name (str): название конфигурации
            search (str, optional): параметры запроса. Defaults to "".

        Returns:
            any: json объект или bool
        """
        params = {
            'search': search
        }
        url = self.url + f'/get_config/{config_name}'
        data, err = self.request.get(url, params)

        data_json = self._is_json(data)
        if err is None and data_json is not False:
            data = data_json
        else:
            data = False
        
        return data

    def add_peer(self, config_name: str, data: dict) -> any:
        """_summary_

        Args:
            config_name (str): название конфигурации
            data (dict): необходимые предварительные параметры

        Returns:
            any: json объект или bool
        """
        if utils.check_param_peer_data(data) is False:
            raise ValueError('invalid data')
        params = utils.create_data_for_add_peer()
        params['name'] = data['username']

        avaliable_ip = self._available_ips(config_name)
        if avaliable_ip == '':
            raise ValueError('no allowed ips')
        params['allowed_ips'] = avaliable_ip

        url = self.url + f'/add_peer/{config_name}'
        data, err = self.request.post(url, params)

        if err is None:
            data = True if data.text == 'true' else False
        else:
            data = False

        return data, params

    def remove_peer(self, config_name: str, peer_ids: list[str]) -> any:
        """удаление аккаунтов

        Args:
            config_name (str): название конфигурации
            peer_ids (list[str]): список из публичных ключей, которые необходио удалить

        Returns:
            _type_: json объект или bool
        """
        params = {
            'action': 'delete',
            'peer_ids': peer_ids,
        }

        url = self.url + f'/remove_peer/{config_name}'
        data, err = self.request.post(url, params)

        if err is None:
            data = True if data.text == 'true' else False
        else:
            data = False

        return data

    def get_peer_data(self, config_name: str, peer_id: str) -> any:
        """получает информацию конфкретного соединения

        Args:
            config_name (str): название конфигурации
            peer_id (str): публичный ключ соединения

        Returns:
            any: json объект или bool
        """
        params = { 'id': peer_id }

        url = self.url + f'/get_peer_data/{config_name}'
        data, err = self.request.post(url, params)

        data_json = self._is_json(data)
        if err is None and data_json is not False:
            data = data_json
        else:
            data = False
        
        return data

    def qrcode(self, config_name: str, peer_id: str) -> str:
        """qr код соединения

        Args:
            config_name (str): название конфигурации
            peer_id (str): публичный ключ соединения

        Returns:
            any: строка изображения
        """
        params = { 'id': peer_id }

        url = self.url + f'/qrcode/{config_name}'
        data, err = self.request.get(url, params)

        if err is None:
            data = data.text if 'data:image/png' in data.text else False
        else:
            data = False
        
        return data

    def download(self, config_name: str, peer_id: str) -> any:
        """получение всех параметров соединения в формате json

        Args:
            config_name (str): название конфигурации
            peer_id (str): публичный ключ соединения

        Returns:
            any: json объект или bool
        """
        params = { 'id': peer_id }

        url = self.url + f'/download/{config_name}'
        data, err = self.request.get(url, params)

        data_json = self._is_json(data)
        if err is None and data_json is not False:
            data = data_json
        else:
            data = False
        
        return data
    