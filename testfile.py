
import json
from cryptography.fernet import Fernet
import cfg
import os

config = '/Users/Loshkarev/Downloads/cfg.json'
cfg_crypt = '/Users/Loshkarev/Downloads/cfg_crypt.json'

# запись конфига при закрытии проги
# запись конфига при сохранении настроек


def encrypt_cfg(data):
    key = Fernet(cfg.KEY)
    encrypted = key.encrypt(data)

    with open(os.path.join(cfg.CFG_DIR, 'cfg.json'), 'wb') as file:
        file.write(encrypted)


def decrypt_cfg():
    key = Fernet(cfg.KEY)

    with open(os.path.join(cfg.CFG_DIR, 'cfg.json'), 'rb') as file:
        data = file.read()

    return json.loads(key.decrypt(data).decode("utf-8"))
