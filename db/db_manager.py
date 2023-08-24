import psycopg2
import psycopg2.extras

class DataBaseManager():

    def __init__(self, dbname: str, user: str, password=None):
        self.conn = psycopg2.connect(f'dbname={dbname} user={user} password={password}')

    def __del__(self):
        self.conn.close()

    def _execute(self, command: str, values = None):
        with self.conn:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(command, values or [])
            return cursor
        
    def create_table(self, table_name: str, columns: dict, extra=None) -> None:
        query = f'CREATE TABLE IF NOT EXISTS {table_name} ('
        colums_with_types = [
            f'{column_name} {data_type}'
            for column_name, data_type in columns.items()
        ]
        query += ', '.join(colums_with_types)
        if extra:
            query += f', {extra}'
        query += ')'
        self._execute(query)

    def add(self, table_name: str, data: dict) -> None:
        placeholders = ', '.join('%s' * len(data))
        column_names = ', '.join(data.keys())
        column_values = tuple(data.values())

        self._execute(
            f'''
            INSERT INTO {table_name}
            ({column_names})
            VALUES ({placeholders});
            ''',
            column_values
        )
    
    def delete (self, table_name: str, criteria: dict) -> None:
        placeholders = [f'{column} = %s' for column in criteria.keys()]
        delete_criteria = ' AND '.join(placeholders)
        self._execute(
            f'''
            DELETE FROM {table_name}
            WHERE {delete_criteria};
            ''',
            tuple(criteria.values()),
        )

    def select(self, table_name: str, criteria=None, order_by=None, limit=100):
        criteria = criteria or {}
        
        query = f'SELECT * FROM {table_name}'

        if criteria:
            placeholders = [f'{column} = %s' for column in criteria.keys()]
            select_criteria = ' AND '.join(placeholders)
            query += f' WHERE {select_criteria}'

        if order_by:
            query += f' ORDER BY {order_by}'
        
        query += f' LIMIT {limit}'

        return self._execute(
            query,
            tuple(criteria.values())
        )
    
    def update(self, table_name: str, data: dict, criteria=None) -> None:
        criteria = criteria or {}

        query = f'UPDATE {table_name} SET'
        column_names = ' = %s, '.join(data.keys())
        column_names += ' = %s'
        query += column_names
        column_values = tuple(data.values())

        if criteria:
            placeholders = [f'{column} = %s' for column in criteria.keys()]
            select_criteria = ' AND '.join(placeholders)
            query += f' WHERE {select_criteria}'

        self._execute(
            query,
            column_values
        )
    