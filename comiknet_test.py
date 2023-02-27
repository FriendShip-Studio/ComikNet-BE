from time import sleep
import pytest
import requests
import os

def test_login():
    username = os.getenv("username")
    password = os.getenv("password")

    res = requests.get("http://localhost:8000/login", data={
        "username": username,
        "password": password
    })

    assert res.status_code == 200
    print(res.text)

if __name__ == "__main__":
    test_login()

