from databse import Database
from utils import extract_json

def init():
    config = extract_json()

    sub_conf = config["sql_connection_settings"]
    Database(
        sub_conf["username"],
        sub_conf["password"],
        sub_conf["host"],
        sub_conf["database"]
        )

init()