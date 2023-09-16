from .init import db
from .exeption import HostOrUserNotExist, PeerAlreadyExist
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
import json

class AddPeer:
    "Добавление нового соединения"
    def execute(self, client_id: int, host_id: int, params: dict) -> None:
        """
        Args:
            client_id (int): id клиента
            host_id (int): id хоста_
            params (dict): json файл с параметрами соединения

        Raises:
            ValueError: json файл не соответсвует шаблону
            HostOrUserNotExist: пользователя или хоста не существует
            PeerAlreadyExist: такое соединение уже создано
        """
        if type(params) != dict:
            raise ValueError('Params is not Valid')
        
        try:
            db.add('peers', {
                'client_id': client_id,
                'host_id': host_id,
                'params': json.dumps(params)
            })
        except ForeignKeyViolation:
            raise HostOrUserNotExist()
        except UniqueViolation:
            raise PeerAlreadyExist()

class RemovePeer:
    "Удаление соединения"
    def execute(self, client_id: int, host_id: int) -> None:
        """
        Args:
            client_id (int): id клиента
            host_id (int): id хоста_
        """
        db.delete('peers', {'client_id': client_id, 'host_id': host_id})

class GetPeerByClientId:
    "Получить все соединения у конкретного клиента"
    def execute(self, client_id: int) -> list:
        """
        Args:
            client_id (int): id клиента

        Returns:
            list: список всех соединений
        """
        peers = db.select('peers', {'client_id': client_id}).fetchall()
        res = [dict(peer) for peer in peers]
        return res

class GetPeerById:
    "Получение одного соединения по (client_id, host_id)"
    def execute(self, client_id: int, host_id: int) -> list:
        """
        Args:
            client_id (int): id клиента
            host_id (int): id хоста_

        Returns:
            list: список, состоящий из параметросоединения
        """
        return db.select('peers', {'client_id': client_id, 'host_id': host_id}).fetchone()
