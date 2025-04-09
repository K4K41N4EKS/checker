def test_successful_login(test_client, registered_user, logged_user):
    assert "access-token" in logged_user.headers, \
        f"Expected access-token not found. Response: {logged_user.json()}"

    assert "refresh-token" in logged_user.headers, \
        f"Expected refresh-token not found. Response: {logged_user.json()}"


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
    refresh_token = logged_user.headers["refresh-token"]
    response = test_client.get(
        f"{app_url}/templates",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    

def test_refresh(test_client, registered_user, logged_user, auth_url, app_url):
    response = test_client.post(
        f"{auth_url}/updateaccesst",
        headers={
            "refresh-token" : logged_user.headers["refresh-token"]}
    )
    
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    
    refresh_token = logged_user.headers["refresh-token"]
    response = test_client.get(
        f"{app_url}/templates",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"
    

def test_logout(test_client, registered_user, logged_user, auth_url, test_user):
    response = test_client.post(
        f"{auth_url}/logout",
        headers={
            "refresh-token" : logged_user.headers["refresh-token"]}
    )
    
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. Response: {response.json()}"