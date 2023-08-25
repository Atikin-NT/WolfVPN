from .init import db

class GetHostById:
    "Получить значения хоста по id"
    def execute(self, host_id: int) -> list:
        """
        Args:
            host_id (int): id хоста в бд

        Returns:
            list: список параметров конкретного хоста
        """
        return db.select('hosts', {'id': host_id}).fetchone()
    
class GetAllHosts:
    "Получить список всех хостов"
    def execute(self) -> list:
        """
        Returns:
            list: список всех хостов
        """
        return db.select('hosts').fetchall()