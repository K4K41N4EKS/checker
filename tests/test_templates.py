from src.python.schemas.template_schema import ValidatedTemplateResponse
import pytest


def test_create_valid_template(test_client, logged_user, app_url, created_template):
    assert created_template.status_code in (200, 201), \
        f"Expected 200 or 201, got {created_template.status_code}. Response: {created_template.json()}"
    try:
        created_template = ValidatedTemplateResponse(**created_template.json())
    except Exception as e:
        pytest.fail(f"Invalid created template structure: {str(e)}")


def test_get_templates(test_client, logged_user, app_url, created_template):
    response = test_client.get(
        f"{app_url}/templates",
        headers=logged_user.auth_header
    )
    
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    
    # Валидация ответа
    try:
        templates = response.json()
        assert isinstance(templates, list), "Response should be a list"
        
        for template in templates:
            validated = ValidatedTemplateResponse(**template)
            assert validated.id, "Template should have ID"
            assert validated.user_id, "Template should have user_id"
    except Exception as e:
        pytest.fail(f"Invalid template structure: {str(e)}")


# def test_create_invalid_template(test_client, logged_user, app_url, invalid_template_data):
#     response = test_client.post(
#         f"{app_url}/templates",
#         json=invalid_template_data,
#         headers=logged_user.auth_header
#     )
    
#     # Ожидаем ошибку валидации (422 или 400 в зависимости от вашего API)
#     assert response.status_code in (400, 422), \
#         f"Expected 400 or 422 for invalid data, got {response.status_code}"


# Дополнить всеми маршрутами
def test_unauthorized_access(test_client, app_url, valid_template_data):
    # GET без авторизации
    response = test_client.get(f"{app_url}/templates")
    assert response.status_code == 403, \
        f"Expected 403 for unauthorized GET, got {response.status_code}"
    
    # POST без авторизации
    response = test_client.post(
        f"{app_url}/templates",
        json=valid_template_data
    )
    assert response.status_code == 403, \
        f"Expected 403 for unauthorized POST, got {response.status_code}"
    

def test_template_get_one(test_client, logged_user, app_url, created_template):
    template_id = created_template.json()["id"]
    
    response = test_client.get(
        f"{app_url}/templates/{template_id}",
        headers=logged_user.auth_header
    )
    
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    
    # Валидация ответа
    try:
        template = response.json()
        validated = ValidatedTemplateResponse(**template)
        assert validated.id, "Template should have ID"
        assert validated.user_id, "Template should have user_id"
            
    except Exception as e:
        pytest.fail(f"Invalid template structure: {str(e)}")


def test_template_update_one(test_client, logged_user, app_url, valid_template_data, created_template):
    template_id = created_template.json()["id"]
    
    # Тест валидного обновления
    valid_update = valid_template_data
    valid_update["name"] = "Updated Template"
    response = test_client.put(
        f"{app_url}/templates/{template_id}",
        json=valid_update,
        headers=logged_user.auth_header
    )
    assert response.status_code == 200, \
        f"Expected 200 for valid update, got {response.status_code}"
    
    # # Тест невалидного обновления
    # invalid_update = valid_template_data
    # invalid_update["filters"] = {"margins": {"top": "invalid"}}
    # response = test_client.patch(
    #     f"{app_url}/templates/{template_id}",
    #     json=invalid_update,
    #     headers=logged_user.auth_header
    # )
    # assert response.status_code == 405, \
    #     f"Expected error for invalid update, got {response.status_code}"


def test_template_delete_one(test_client, logged_user, app_url, created_template):
    template_id = created_template.json()["id"]
    
    # Проверка перед удалением
    response = test_client.get(
        f"{app_url}/templates/{template_id}",
        headers=logged_user.auth_header
    )
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    
    # Удаление
    response = test_client.delete(
        f"{app_url}/templates/{template_id}",
        headers=logged_user.auth_header
    )
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"

    # Проверка после удаления
    response = test_client.get(
        f"{app_url}/templates/{template_id}",
        headers=logged_user.auth_header
    )
    assert response.status_code == 404, \
        f"Expected 404, got {response.status_code}. Response: {response.json()}"