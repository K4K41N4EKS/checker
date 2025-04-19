#include "_database.h"


_database::database::database() {

    configdb::ServisConfig servisCfg = configdb::ServisConfig(
        std::string(getenv("AUTH_SERVIS_DB_DIR"))
    );
    
    connectionArguments = servisCfg.getConnectionArgs();

}

void _database::database::q_registration_insert(std::string userid, std::string username, std::string password) {

    try
    {
        
        pqxx::connection conn(connectionArguments);
        pqxx::work transaction(conn);

        auto result = transaction.exec(
            "INSERT INTO users (user_id, username, password_hash) VALUES (" + 
            transaction.quote(userid) + ", " +
            transaction.quote(username) + ", " +
            transaction.quote(drogon::utils::getSha256(password)) + ")"
        );
        if (!result.empty()) {
            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::RegistrationModule_UsernameIsAlreadyTaken
            );
        }
        transaction.commit();

    }
    catch(const std::exception &e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::RegistrationModule_UsernameIsAlreadyTaken
        );
    }
    catch(const authServisErrors::AuthServisException& e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::RegistrationModule_UsernameIsAlreadyTaken
        );
    }
    

}

void _database::database::q_registration_delete(std::string userid) {

    try
    {
        
        pqxx::connection conn(connectionArguments);
        pqxx::work transaction(conn);

        auto result = transaction.exec(
            "DELETE FROM users WHERE user_id = " + 
            transaction.quote(userid) + ";"
        );
        if (!result.empty()) {
            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::RegistrationModule_CantDeleteUser
            );
        }
        transaction.commit();

    }
    catch(const std::exception &e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::DatabaseModule_pqxxError
        );
    }
    catch(const authServisErrors::AuthServisException& e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::RegistrationModule_CantDeleteUser
        );
    }
    

}

void _database::database::q_updateaccess_select_username_and_refresh(std::string username, std::string refreshToken) {

    try
    {
        
        pqxx::connection conn(connectionArguments);
        pqxx::work transaction(conn);

        auto result = transaction.exec(
            "SELECT * FROM users WHERE username = " + 
            transaction.quote(username) +
            " AND refresh_token = " + 
            transaction.quote(refreshToken) + ";"
        );
        if(result.empty()){

            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::UpdateAccessModule_UnregisteredRefreshToken
            );
        
        }
        transaction.commit();

    }
    catch(const std::exception &e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::DatabaseModule_pqxxError
        );
    }
    catch(const authServisErrors::AuthServisException& e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::UpdateAccessModule_UnregisteredRefreshToken
        );
    }

}

void _database::database::q_logout_select_username_and_refresh(std::string username, std::string refreshToken) {

    try
    {
        
        pqxx::connection conn(connectionArguments);
        pqxx::work transaction(conn);

        auto result = transaction.exec(
            "SELECT * FROM users WHERE username = " + 
            transaction.quote(username) +
            " AND refresh_token = " + 
            transaction.quote(refreshToken) + ";"
        );
        if(result.empty()){

            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::LogoutModule_UnauthorizedUser
            );
        
        }
        transaction.commit();

    }
    catch(const std::exception &e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::DatabaseModule_pqxxError
        );
    }
    catch(const authServisErrors::AuthServisException& e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::LogoutModule_UnauthorizedUser
        );
    }

}

void _database::database::q_logout_update(std::string username, std::string refreshToken) {

    try
    {
        
        pqxx::connection conn(connectionArguments);
        pqxx::work transaction(conn);

        auto result = transaction.exec(
            "UPDATE users SET access_token = '', "
            "refresh_token = '' WHERE username = " + 
            transaction.quote(username) + " AND refresh_token = " +
            transaction.quote(refreshToken) + ";"
        );
        if(result.empty()){

            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::LogoutModule_CantDeleteTokens
            );
        
        }
        transaction.commit();

    }
    catch(const std::exception &e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::DatabaseModule_pqxxError
        );
    }
    catch(const authServisErrors::AuthServisException& e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::LogoutModule_CantDeleteTokens
        );
    }

}

void _database::database::q_login_select(std::string username, std::string password) {

    try
    {
        
        pqxx::connection conn(connectionArguments);
        pqxx::work transaction(conn);

        auto result = transaction.exec(
            "SELECT * FROM users WHERE username = " + 
            transaction.quote(username) + 
            " AND password_hash = " +
            transaction.quote(drogon::utils::getSha256(password)) + ";"
        );
        if(result.empty()){

            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::LoginModule_IncorrectSignInData
            );
        
        }
        transaction.commit();

    }
    catch(const std::exception &e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::DatabaseModule_pqxxError
        );
    }
    catch(const authServisErrors::AuthServisException& e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::LoginModule_IncorrectSignInData
        );
    }

}


