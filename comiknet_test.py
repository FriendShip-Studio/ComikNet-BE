import pytest
import requests
import json
import os

def test_login():
    username = os.getenv("username")
    password = os.getenv("password")

    res = requests.post("http://localhost:8000/login", data=json.dumps({
        "username": username if username else "admin",
        "password": password if password else "admin"
    }))
    
    assert res.status_code == 200

if __name__ == "__main__":
    test_login()

