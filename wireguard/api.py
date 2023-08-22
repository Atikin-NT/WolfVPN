from session import Request

class API:

    def __init__(self, password: str, username: str, login_url: str) -> None:
        self.request = Request(password, username, login_url)

    def get_config(self, config_name: str, search=""):
        pass

    def add_peer(self, config_name: str, data: dict):
        pass

    def remove_peer(self, config_name: str, peer_ids: list[str]):
        pass

    def get_peer_data(self, configuration: str, id: str):
        pass

    def available_ips(self, configuration: str):
        pass

    def check_key_match(self, configuration: str):
        pass

    def qrcode(self, configuration: str, id: str):
        pass

    def download(self, configuration: str, id: str):
        pass

    