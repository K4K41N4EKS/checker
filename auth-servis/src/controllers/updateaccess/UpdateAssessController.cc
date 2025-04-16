#include "UpdateAssessController.h"
#include "ServisConfig.h"
#include "_auth-servisError.h"

#include <drogon/drogon.h>
#include <jsoncpp/json/json.h>
#include <pqxx/pqxx>
#include <cstdlib>



void UpdateAssessController::updateAccessToken(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback){
    
    auto headers = (*req).getHeaders();

    try
    {
        if (headers.empty() || 
            headers.find("refresh-token") == headers.end() || 
            headers["refresh-token"].empty() ||
            headers["refresh-token"] == ""){

            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::UpdateAccessModule_EmptyRefreshToken
            );
        }
    }
    catch(const authServisErrors::AuthServisException& e)
    {
        Json::Value err;
        err["status"] = "error";
        err["message"] = e.what();

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(e.ToDrogonHttpErrorCode());
        
        callback(response);
        return;
    }
    

    std::string refreshToken = headers["refresh-token"];
    std::string username = getUsernameFromToken(refreshToken);

    try
    {


        configdb::ServisConfig servisCfg = 
            configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));


        pqxx::connection conn(servisCfg.getConnectionArgs());
        pqxx::work userExistenceCheck_Txn(conn);

        auto result = userExistenceCheck_Txn.exec(
            "SELECT * FROM users WHERE username = " + 
            userExistenceCheck_Txn.quote(username) +
            " AND refresh_token = " + 
            userExistenceCheck_Txn.quote(refreshToken) + ";"
        );
        if(result.empty()){

            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::UpdateAccessModule_UnregisteredRefreshToken
            );
        
        }
        userExistenceCheck_Txn.commit();

        validateRefreshToken(refreshToken);

        std::string token = generateAndCommitAccessToken(username);

        Json::Value resp;
        resp["status"] = "success";
        resp["message"] = "Token update successfuly";

        auto response = drogon::HttpResponse::newHttpJsonResponse(resp);
        response->setStatusCode(drogon::HttpStatusCode::k201Created)
        response->addHeader("access-token", token);
        callback(response);

    }
    catch(const authServisErrors::AuthServisException& e)
    {
        Json::Value err;
        err["status"] = "error";
        err["message"] = e.what();

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(e.ToDrogonHttpErrorCode());
        
        callback(response);
    }

}

