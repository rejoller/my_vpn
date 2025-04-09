import ctypes
import pandas as pd
from icecream import ic
from bot.config import API_ADDRESS, API_PORT, GO_FILE_PATH, EMAIL, UUID

lib = ctypes.CDLL(GO_FILE_PATH)



address = f"{API_ADDRESS}:{API_PORT}"

lib.InitClient.argtypes = [ctypes.c_char_p]

lib.InitClient(address.encode('utf-8'))  # сначала инициализируем клиента

# Указываем, что addUser ожидает два параметра типа c_char_p
lib.addUser.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.addUser.restype = ctypes.c_char_p
lib.getUsers.restype = ctypes.c_char_p


users = lib.getUsers()





# Передаем параметры в функцию
# add_result = lib.addUser(email.encode('utf-8'), user_id.encode('utf-8'))

ic(users.decode())

df = pd.DataFrame()

# print(add_result)

