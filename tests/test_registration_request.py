def test_registration(test_client, registered_user):
    assert registered_user.status_code == 200, \
        f"Expected 200, got {registered_user.status_code}. Response: {registered_user.json()}"
    
    # service_db_user = service_db.query(User).order_by(User.id.desc()).first()
    # app_db_user = app_db.query(User).order_by(User.id.desc()).first()
    
    # assert app_db_user.id is not None, "User ID missing in app DB"
    # assert app_db_user.username == "test", f"Expected username 'test', got {app_db_user.username}"
    
    # # Repeat for service_db (ensure it's also a Session)
    # assert service_db_user.user_id == app_db_user.id, "ID mismatch between DBs"

def test_registration_second_attempt(test_client, auth_url, test_user):
    response = test_client.post(
        f"{auth_url}/registration",
        headers={
            "username": test_user["username"], 
            "passwd": test_user["password"]}
    )
    
    assert response.status_code == 500, \
        f"Expected 500, got {response.status_code}. Response: {response.json()}"
    
