import requests
import pytest
from src.python.database.database import SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.python.models.user import User

@pytest.fixture(scope="session")
def test_client():
    return requests.Session()

@pytest.fixture(scope="session")
def auth_url():
    return "http://0.0.0.0:3333"

@pytest.fixture(scope="session")
def app_url():
    return "http://0.0.0.0:3000"

@pytest.fixture(scope="session")
def test_user() -> dict[str, str]:
    return {
        "username": "test",
        "password": "123654"
    }

@pytest.fixture(scope="session")
def registered_user(auth_url, test_user):
    # Регистрируем пользователя перед тестами
    response = requests.post(
        f"{auth_url}/registration",
        headers={
            "username": test_user["username"], 
            "passwd": test_user["password"]}
    )
    
    yield response
    # Здесь можно добавить очистку, если API предоставляет удаление пользователя

@pytest.fixture
def logged_user(registered_user, auth_url, test_user):
    """Фикстура, которая логинит пользователя и возвращает токены, очищая refresh после тестов"""
    
    response = requests.get(
        f"{auth_url}/login",
        headers={
            "username": test_user["username"], 
            "passwd": test_user["password"]}
    )

    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    
    tokens = response
    
    yield tokens  # Возвращаем токены тестам
    
    # Пост-обработка: выполняем логаут после завершения тестов
    requests.post(
        f"{auth_url}/logout",
        headers={"Authorization": f"Bearer {tokens.headers['refresh-token']}"}
    )
    