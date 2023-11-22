from envparse import env, Env

env = Env()
env.read_envfile()

# BOT
TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_BOT_TOKEN')
LOGFILE = env.str('LOGFILE')

# SERVER
SERVER_HOST = env.str('SERVER_HOST')
SERVER_PORT = env.str('SERVER_PORT')

# DATABASE
POSTGRES_HOST = env.str('POSTGRES_HOST', default='localhost')
POSTGRES_PORT = env.int('DB_PORT', default=5432)
POSTGRES_USER = env.str('POSTGRES_USER', default='postgres')
POSTGRES_PASSWORD = env.str('POSTGRES_PASSWORD', default=None)
POSTGRES_DB = env.str('POSTGRES_DB')

DEFAULT_ADMIN = env.int('DEFAULT_ADMIN')