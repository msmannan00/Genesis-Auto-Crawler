import base64
import time
from fernet import Fernet

from crawler.crawler_services.shared.env_handler import env_handler


class crypto_handler:
    def __init__(self):
        self.fernet_key = env_handler.get_instance().env('S_FERNET_KEY')
        self.app_block_key = env_handler.get_instance().env('S_APP_BLOCK_KEY')

    def generate_secret_token(self):
        fernet = Fernet(base64.urlsafe_b64encode(self.fernet_key.encode()))
        secret_data = f"{self.app_block_key}----{int(time.time())}"
        return fernet.encrypt(secret_data.encode()).decode()
