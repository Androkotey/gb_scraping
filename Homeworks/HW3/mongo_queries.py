def salary_filter(collection, value, option='$gte'):
    """ Переводит валюту в рубли, создаёт соответствующие поля и фильтрует результат """

    return collection.aggregate([
        {
            '$fill':  # Заполнение None
                {
                    'output':
                        {
                            'salary_min': {'value': 0},
                            'salary_max': {'value': 0},
                        }
                }
        },
        {
            '$addFields':  # Конвертация валюты
                {
                    'salary_min_rub': {'$switch': {
                        'branches': [
                            {'case': {'$eq': ['$salary_currency', 'бел.руб.']}, 'then':
                                {'$multiply': ['$salary_min', 30]}},
                            {'case': {'$eq': ['$salary_currency', 'руб.']}, 'then':
                                {'$multiply': ['$salary_min', 1]}},
                            {'case': {'$eq': ['$salary_currency', 'USD']}, 'then':
                                {'$multiply': ['$salary_min', 65]}},
                            {'case': {'$eq': ['$salary_currency', 'EUR']}, 'then':
                                {'$multiply': ['$salary_min', 70]}},
                            {'case': {'$eq': ['$salary_currency', 'сум']}, 'then':
                                {'$multiply': ['$salary_min', 0.0053]}},
                            {'case': {'$eq': ['$salary_currency', 'KZT']}, 'then':
                                {'$multiply': ['$salary_min', 0.14]}}
                        ],
                        'default': None}},
                    'salary_max_rub': {'$switch': {
                        'branches': [
                            {'case': {'$eq': ['$salary_currency', 'бел.руб.']}, 'then':
                                {'$multiply': ['$salary_max', 30]}},
                            {'case': {'$eq': ['$salary_currency', 'руб.']}, 'then':
                                {'$multiply': ['$salary_max', 1]}},
                            {'case': {'$eq': ['$salary_currency', 'USD']}, 'then':
                                {'$multiply': ['$salary_max', 65]}},
                            {'case': {'$eq': ['$salary_currency', 'EUR']}, 'then':
                                {'$multiply': ['$salary_max', 70]}},
                            {'case': {'$eq': ['$salary_currency', 'сум']}, 'then':
                                {'$multiply': ['$salary_max', 0.0053]}},
                            {'case': {'$eq': ['$salary_currency', 'KZT']}, 'then':
                                {'$multiply': ['$salary_max', 0.14]}}
                        ],
                        'default': None}}}},
        {
            '$match':  # Фильтрация
                {
                    '$or': [{'salary_min_rub': {option: value}}, {'salary_max_rub': {option: value}}]
                }
        }])
