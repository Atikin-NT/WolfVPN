class ClientAlreadyExist(Exception):
    "Клиент с таким индексом уже существует"

class ClientNotExist(Exception):
    "Клиента с таким индексом не существует"

class HostNotExist(Exception):
    "Хоста с таким индексом не существует"

class PeerAlreadyExist(Exception):
    "такое соединение уже существует"

class HostOrUserNotExist(Exception):
    "пользователь или хост не существует"

class NotEnoughMoney(Exception):
    "Недостаточно средств на счету пользователя"