from .init import db
from psycopg2.errors import UniqueViolation
from .exeption import ClientAlreadyExist

class AddClient:
    "Добавить нового клиента"
    def execute(self, client_id: int, name: str):
        """
        Args:
            client_id (int): id клиента
            name (str): имя клиента

        Raises:
            ValueError: имя не может быть пустым
        """
        if name.strip() == '':
            raise ValueError('Empty name')
        try:
            db.add('clients', {'id': client_id, 'name': name})
        except UniqueViolation:
            raise ClientAlreadyExist('Client already exist')

class UpdateClientAmount:
    "Обновить балан клиента"
    def execute(self, client_id: int, amount: int):
        """
        Args:
            client_id (int): id клиента в телеге
            amount (int): новая сумма на счету

        Raises:
            ValueError: новое значение суммы не может быть меньше нуля
        """
        if amount < 0:
            raise ValueError('Amount can not be below zero')
        db.update(
            'clients', 
            {'amount': amount},
            {'id': client_id}
        )

class GetClientById:
    "Получить данные о клиенте"
    def execute(self, client_id: int):
        """
        Args:
            client_id (int): id клиента в телеге

        Returns:
            _type_: результат в виде словаря или None, если такого не существует
        """
        return db.select('clients', {'id': client_id}).fetchone()


class GetAllClients:
    "Получить список всех клиентов"
    def execute(self):
        """
        Returns:
            list: список всех пользователей
        """
        clients = db.select('clients').fetchall()
        res = [dict(client) for client in clients]
        return res