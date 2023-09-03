from db.db_manager import DataBaseManager
import configparser

config = configparser.ConfigParser()
config.read('./config.ini')
bot_config = config['database']

db = DataBaseManager(bot_config['dbname'], bot_config['user'], bot_config['password'])

class CreateTable:
    def execute(self) -> None:
        db.create_table('clients', {
            'id': 'bigint not null PRIMARY KEY',
            'name': 'text',
            'amount': 'integer not null default 0',
            'join_date': 'date not null default CURRENT_DATE',
        })
        db.create_table('pay_history', {
            'id': 'serial PRIMARY KEY',
            'client_id': 'bigint REFERENCES clients( id )',
            'amount': 'integer not null',
            'status': 'integer not null default 0',
            'create_date': 'date not null default CURRENT_DATE'
        })
        db.create_table('hosts', {
            'id': 'serial PRIMARY KEY',
            'main_url': 'text not null',
            'login_url': 'text not null',
            'password': 'text not null',
            'username': 'text not null',
            'region': 'text not null'
        })
        db.create_table('peers', {
            'client_id': 'bigint REFERENCES clients( id )',
            'host_id': 'integer references hosts ( id )',
            'create_date': 'date not null default CURRENT_DATE',
            'params': 'jsonb not null'
            }, 'PRIMARY KEY (client_id, host_id)')
        db.create_table('codes', {
            'code': 'serial PRIMARY KEY',
            'amount': 'int not null',
            'activated': 'bool default false'
        })