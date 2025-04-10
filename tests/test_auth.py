def test_successful_login(test_client, registered_user, logged_user):
    assert logged_user.access_token, "Access token not found"
    assert logged_user.refresh_token, "Refresh token not found"


def test_login_with_wrong_password(test_client, registered_user, auth_url, test_user):
    response = test_client.get(
        f"{auth_url}/login",
        headers={
            "username": test_user["username"], 
            "passwd": "12354"}
    )
    
    assert response.status_code == 401, \
        f"Expected 401, got {response.status_code}. Response: {response.json()}"
    
    status = response.json()["status"]
    assert status == "error", \
        f"Expected status:error, got {status}. Response: {response.json()}"


def test_access(test_client, registered_user, logged_user, app_url):
    response = test_client.get(
        f"{app_url}/templates",
        headers=logged_user.auth_header
    )

    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    

def test_refresh(test_client, registered_user, logged_user, auth_url, app_url):
    response = test_client.post(
        f"{auth_url}/updateaccesst",
        headers=logged_user.refresh_header
    )
    
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    
    response = test_client.get(
        f"{app_url}/templates",
        headers=logged_user.auth_header
    )

    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    

def test_logout(test_client, registered_user, logged_user, auth_url, test_user):
    response = test_client.post(
        f"{auth_url}/logout",
        headers=logged_user.refresh_header
    )
    
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    