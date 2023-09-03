from .init import db
from psycopg2.errors import ForeignKeyViolation
from .exeption import ClientNotExist

class AddBill:
    "Создание нового чека в системе"
    def execute(self, client_id: int, amount: int) -> int:
        """
        Args:
            client_id (int): id клиента
            amount (int): сумма на чеке

        Raises:
            ValueError: значение чека меньше или равна нулю
            ClientNotExist: Не существует клиента, на который хотят повеить чек

        Returns:
            int: id чека в таблице
        """
        if amount <=0:
            raise ValueError("Amount below zero")
        try:
            bill_id = db.add('pay_history', {'client_id': client_id, 'amount': amount}, 'id').fetchone()[0]
        except ForeignKeyViolation:
            raise ClientNotExist()
        return int(bill_id)

class UpdateBillStatus:
    "Обновление статуса чека"
    def execute(self, bill_id: int, status: int):
        """
        Args:
            bill_id (int): id чека
            status (int): новый статус. 0-чек создан. 1-деньги отправлены. 2-деньги получены.

        Raises:
            ValueError: статус не соответствует нужным значениям
        """
        if status not in [0, 1, 2]:
            raise ValueError("Invalid status")
        
        db.update(
            'pay_history',
            {'status': status},
            {'id': bill_id}
        )

class GetClietnHistory:
    "Получение истории операций пользователя"
    def execute(self, client_id: int):
        """_summary_

        Args:
            client_id (int): id клиента

        Returns:
            list: список всех операций
        """
        bills = db.select(
                'pay_history', 
                {'client_id': client_id}
            ).fetchall()
        res = [dict(bill) for bill in bills]
        return res