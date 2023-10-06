from .db_manager import Connection

class GetHostById(Connection):
    "Получить значения хоста по id"
    def execute(self, host_id: int) -> list:
        """
        Args:
            host_id (int): id хоста в бд

        Returns:
            list: список параметров конкретного хоста
        """
        return Connection.db.select('hosts', {'id': host_id}).fetchone()
    
class GetAllHosts(Connection):
    "Получить список всех хостов"
    def execute(self) -> list:
        """
        Returns:
            list: список всех хостов
        """
        hosts = Connection.db.select('hosts').fetchall()
        res = [dict(host) for host in hosts]
        return res