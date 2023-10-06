from .db_manager import Connection

class GetCode(Connection):
    "Получить параметры кода по его значению"
    def execute(self, code: str):
        """
        Args:
            code (str): сам код

        Returns:
            _type_: None если код не найден, иначе - список из его параметров
        """
        return Connection.db.select('codes', {'code': code}).fetchone()
    
class ActivateCode(Connection):
    "Активация кода"
    def execute(self, code: str):
        """
        Args:
            code (int): сам код
        """
        Connection.db.update('codes', {'activated': True}, {'code': code})