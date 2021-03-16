from os import environ
from yaml import load, FullLoader

from constants import CRED_FILE_OR_ENVIRON, CRED_FILE_NAME


def get_cred():

    if CRED_FILE_OR_ENVIRON == "file":
        try:
            with open(CRED_FILE_NAME, "r") as cred_file_obj:
                cred = load(cred_file_obj.read(), Loader=FullLoader)
                cred_file_obj.close()
            return cred
        except FileNotFoundError:
            print(CRED_FILE_NAME, "file does not exists (FileNotFoundError).")
            exit(1)

    elif CRED_FILE_OR_ENVIRON == "environ":

        cred = {
            "mongodb-url": environ.get("MONGODB_URL"),
            "discord-token": environ.get("DISCORD_TOKEN")
        }
        return cred

    else:
        raise ValueError("constants.CRED_OR_ENVIRON is not 'cred' or 'environ'.")
