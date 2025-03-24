#include "auth.h"
#include "ServisConfig.h"


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
        
        throw std::runtime_error("Expired token lifetime");
    }
    
}

std::string authAndValid::IAuth::GenerateJwt(
    const std::string &username,
    const int &hours,
    const int &minutes){

    if(username.empty()){
        throw std::domain_error("User not found");
    }


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
        throw std::domain_error("Bad generation");
    }


    return token;
}


std::string authAndValid::IAuth::generateAndCommitAccessToken(const std::string &username){
    
    if(username.empty()){
        throw std::domain_error("User not found");
    }


    configdb::ServisConfig servisCfg = 
        configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));

    std::string token = GenerateJwt(
                            username, 
                            servisCfg.getAccessTLifestyleTime_hours(),
                            servisCfg.getAccessTLifestyleTime_minuts()
                        );


    pqxx::connection conn(servisCfg.getConnectionArgs());
    pqxx::work txn(conn);

    auto result = txn.exec(
        "UPDATE users SET access_token = " + txn.quote(token) +
        " WHERE username = " + txn.quote(username) + ";"
    );
    if (!result.empty()) {
        throw std::runtime_error("Unexpected result from Update query");
    }
    txn.commit();

    return token;

}

std::string authAndValid::IAuth::generateAndCommitRefreshToken(const std::string &username){
    
    if(username.empty()){
        throw std::domain_error("User not found");
    }


    configdb::ServisConfig servisCfg = 
        configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));

    std::string token = GenerateJwt(
                            username, 
                            servisCfg.getRefreshTLifestyleTime_hours(), 
                            servisCfg.getRefreshTLifestyleTime_minuts()
                        );


    pqxx::connection conn(servisCfg.getConnectionArgs());
    pqxx::work txn(conn);

    auto result = txn.exec(
        "UPDATE users SET refresh_token = " + txn.quote(token) +
        " WHERE username = " + txn.quote(username) + ";"
    );
    if (!result.empty()) {
        throw std::runtime_error("Unexpected result from Update query");
    }
    txn.commit();

    return token;

}

std::string authAndValid::IAuth::getUsernameFromToken(std::string token){

    jwt::decoded_jwt decoded = jwt::decode(token);
    
    return decoded.get_subject();

}
