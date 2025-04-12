import requests
import pytest
from src.python.schemas.user_schema import UserTokens
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
    
    tokens = UserTokens(
        access_token=response.headers["access-token"],
        refresh_token=response.headers["refresh-token"]
    )
    
    yield tokens
    
    # Пост-обработка: выполняем логаут после завершения тестов
    requests.post(
        f"{auth_url}/logout",
        headers=tokens.refresh_header
    )

@pytest.fixture(scope="session")
def valid_template_data():
    return {
        "name": "ГОСТ-2 2024",
        "filters": {
            "start_after_heading": "Оглавление",
            "margins": {
                "top": 2,
                "bottom": 2,
                "left": 3,
                "right": 1.5
            },
            "styles": {
                "Normal": {
                    "font_name": ["Times New Roman"],
                    "font_size": [14],
                    "font_color_rgb": "000000",
                    "bold": False,
                    "italic": False,
                    "underline": False,
                    "all_caps": False,
                    "alignment": "JUSTIFY",
                    "line_spacing": 1.5,
                    "first_line_indent": 1.25
                },
                "Caption": {
                    "font_name": ["Times New Roman"],
                    "font_size": [12],
                    "alignment": "CENTER",
                    "line_spacing": 1
                }
            }
        }
    }

@pytest.fixture(scope="session")
def invalid_template_data():
    return {
        "name": "Invalid Template",
        "filters": {
            "start_after_heading": "Оглавление",
            "margins": {
                "top": "invalid",  # Неправильный тип
                "bottom": 2,
                "left": 3,
                "right": 1.5
            },
            "styles": {}
        }
    }
