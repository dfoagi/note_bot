import os
from dotenv import load_dotenv

load_dotenv(override=True)

BOT_TOKEN = os.getenv('TOKEN')
ADMIN_ID = os.getenv('MAIN_ADMIN')
RATE_LIMIT = int(os.getenv('RATE_LIMIT'))
ADMINS = os.getenv('ADMINS').split(',')
