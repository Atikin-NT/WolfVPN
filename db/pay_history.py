from .init import db
from psycopg2.errors import ForeignKeyViolation

class ClientNotExist(Exception):
    "Клиента с таким индексом не существует"

class AddBill:
    "Создание нового чека в системе"
    def execute(self, client_id: int, amount: int) -> int:
        if amount <=0:
            raise ValueError("Amount below zero")
        try:
            bill_id = db.add('pay_history', {'client_id': client_id, 'amount': amount}, 'id').fetchone()[0]
        except ForeignKeyViolation:
            raise ClientNotExist()
        return int(bill_id)

class UpdateBillStatus:
    def execute(self, bill_id: int, amount: int):
        if amount <= 0:
            raise ValueError("Amount below zero")
        
        db.update(
            'pay_history',
            {'amount': amount},
            {'id': bill_id}
        )

class GetClietnHistory:
    def execute(self, client_id: int):
        return db.select(
            'pay_history', 
            {'client_id': client_id}
        ).fetchall()