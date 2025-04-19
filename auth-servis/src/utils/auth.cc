#include "auth.h"
#include "ServisConfig.h"
#include "_auth-servisError.h"


void authAndValid::IAuth::validateRefreshToken(std::string &token) {


    configdb::ServisConfig servisCfg = 
        configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));


    auto verifier = jwt::verify()
        .with_issuer("auth_servis")
        .allow_algorithm(jwt::algorithm::hs256{servisCfg.getSecretKey()});

    jwt::decoded_jwt decoded = jwt::decode(token);
    std::error_code ec;

    verifier.verify(decoded, ec);

    if (ec) {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::AuthModule_ExpiredTokenLifetime
        );
    }
    
}

std::string authAndValid::IAuth::GenerateJwt(
    const std::string &username,
    const int &hours,
    const int &minutes){


    configdb::ServisConfig servisCfg = 
        configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));


    std::string token = jwt::create()
        .set_issuer("auth_servis")
        .set_subject(username)
        .set_type("JWS")
        .set_payload_claim(
            "username", jwt::claim(username)
        )
        .set_expires_at(

            std::chrono::system_clock::now() +
            std::chrono::hours(hours) +
            std::chrono::minutes(minutes)
        )
        .sign(

            jwt::algorithm::hs256{servisCfg.getSecretKey()}
        );

    if (token.empty()) {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::AuthModule_CantGenerateToken
        );
    }


    return token;
}

std::string authAndValid::IAuth::generateAndCommitAccessToken(const std::string &username){
    
    if(username.empty()){
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::AuthModule_UserNotFound
        );
    }


    configdb::ServisConfig servisCfg = 
        configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));

    std::string token = GenerateJwt(
                            username, 
                            servisCfg.getAccessTLifestyleTime_hours(),
                            servisCfg.getAccessTLifestyleTime_minuts()
                        );


    pqxx::connection conn(servisCfg.getConnectionArgs());
    pqxx::work updateAccessTokenToUser_Txn(conn);

    auto result = updateAccessTokenToUser_Txn.exec(
        "UPDATE users SET access_token = " + 
        updateAccessTokenToUser_Txn.quote(token) +
        " WHERE username = " + 
        updateAccessTokenToUser_Txn.quote(username) + ";"
    );
    if (!result.empty()) {
        updateAccessTokenToUser_Txn.commit();
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::AuthModule_CantUpdateUsersTableWithAccessToken
        );
    }
    updateAccessTokenToUser_Txn.commit();

    return token;

}

std::string authAndValid::IAuth::generateAndCommitRefreshToken(const std::string &username){
    
    if(username.empty()){
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::AuthModule_UserNotFound
        );
    }


    configdb::ServisConfig servisCfg = 
        configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));

    std::string token = GenerateJwt(
                            username, 
                            servisCfg.getRefreshTLifestyleTime_hours(), 
                            servisCfg.getRefreshTLifestyleTime_minuts()
                        );


    pqxx::connection conn(servisCfg.getConnectionArgs());
    pqxx::work updateRefreshTokenToUser_Txn(conn);

    auto result = updateRefreshTokenToUser_Txn.exec(
        "UPDATE users SET refresh_token = " + 
        updateRefreshTokenToUser_Txn.quote(token) +
        " WHERE username = " + 
        updateRefreshTokenToUser_Txn.quote(username) + ";"
    );
    if (!result.empty()) {
        updateRefreshTokenToUser_Txn.commit();
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::AuthModule_CantUpdateUsersTableWithRefreshToken
        );
    }
    updateRefreshTokenToUser_Txn.commit();

    return token;

}

std::string authAndValid::IAuth::getUsernameFromToken(std::string token){

    jwt::decoded_jwt decoded = jwt::decode(token);
    
    try
    {
        std::string username = decoded.get_subject();
        return username;
    }
    catch(const std::exception& e)
    {
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::AuthModule_UsernameClaimIsEmpty
        );
    }
    
}
