TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
USE_SQL = False
DELETE_SQL_DATA = False
USE_REDIS = False
USE_CELERY = False
commodity_names = ['gold', 'oil']
commodity_units = {
    'gold': {
        'price': '$',
        'vol': 'kg'
    },
    'oil': {
        'price': '$',
        'vol': 'L'
    }
}