import os
import ydb

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")

def get_ydb_pool(ydb_endpoint, ydb_database, timeout=30):
    ydb_driver_config = ydb.DriverConfig(
        ydb_endpoint,
        ydb_database,
        credentials=ydb.credentials_from_env_variables(),
        root_certificates=ydb.load_ydb_root_certificate(),
    )

    ydb_driver = ydb.Driver(ydb_driver_config)
    ydb_driver.wait(fail_fast=True, timeout=timeout)
    return ydb.SessionPool(ydb_driver)


def _format_kwargs(kwargs):
    return {"${}".format(key): value for key, value in kwargs.items()}


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_update_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )

    return pool.retry_operation_sync(callee)


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_select_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
        return result_sets[0].rows

    return pool.retry_operation_sync(callee)    

# Зададим настройки базы данных 
pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)


# Структура квиза
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения чисел с плавающей точкой?',
        'options': ['float', 'int', 'str', 'natural'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных относится к неизменяемым типам данных в языке Python?',
        'options': ['str', 'set', 'dict', 'list'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных не может использоваться в качестве ключа в словаре Python?',
        'options': ['list', 'int', 'float', 'str'],
        'correct_option': 0
    },
    {
        'question': 'Что из представленного является списком Python',
        'options': ['[2, 46.5, "Hello"]', 'Hello', '{1, 2, 3}', '(45, 1)'],
        'correct_option': 0
    },
    {
        'question': 'К какому типу языков программирования не относится Python?',
        'options': ['Компилируемый', 'Интерпретируемый', 'Императивный', 'Высокого уровня'],
        'correct_option': 0
    },
    {
        'question': 'Что из предложенного является модулем Python?',
        'options': ['os', 'MySQL', 'MariaDB', 'GUI'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных отсутствует в языке Python?',
        'options': ['char', 'int', 'float', 'str'],
        'correct_option': 0
    },
    {
        'question': 'Какая концепция ООП позволяет применять одни и те же методы к экземплярам различных классов?',
        'options': ['Полиморфизм', 'Инкапсуляция', 'Наследование', 'Абстракция'],
        'correct_option': 0
    },
]
