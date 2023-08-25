from .init import db

class GetCode:
    "Получить параметры кода по его значению"
    def execute(self, code: int):
        """
        Args:
            code (int): сам код

        Returns:
            _type_: None если код не найден, иначе - список из его параметров
        """
        return db.select('codes', {'code': code}).fetchone()
    
class ActivateCode:
    "Активация кода"
    def execute(self, code: int):
        """
        Args:
            code (int): сам код
        """
        db.update('codes', {'activated': True}, {'code': code})