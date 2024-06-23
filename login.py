import json
import os

from dotenv import load_dotenv
from requests import request

from config import base_url

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


def get_token():
    email = os.getenv("API_USER")
    password = os.getenv("API_PWD")

    if not email or not password:
        raise ValueError("Email e senha devem ser definidos nas variáveis de ambiente.")

    payload = json.dumps({"email": email, "password": password})
    headers = {
        "Content-Type": "application/json",
    }

    response = request(
        "POST", base_url + "/api/users/login", headers=headers, data=payload
    )

    if response.status_code != 200:
        raise Exception("Falha ao obter token. Verifique suas credenciais.")

    return response.json()["token"]
