from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
PASSWORD = os.getenv("DB_PASSWORD")
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")
PCCLUB = os.getenv('PCCLUB')
ADMIN = [5851250080, 5638402683, 5946439711]