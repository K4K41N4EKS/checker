#include "UpdateAssessController.h"
#include "ServisConfig.h"

#include <drogon/drogon.h>
#include <jsoncpp/json/json.h>
#include <pqxx/pqxx>
#include <cstdlib>



void UpdateAssessController::updateAccessToken(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback){
    
    auto headers = (*req).getHeaders();

    if (headers.empty() || headers.find("refresh-token") == headers.end() || 
        headers["refresh-token"].empty()){
        Json::Value err;
        err["status"] = "error";
        err["message"] = "Invalid parms";

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(drogon::HttpStatusCode::k401Unauthorized);
        
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
        pqxx::work txn(conn);

        auto result = txn.exec(
            "SELECT * FROM users WHERE username = " + txn.quote(username) +
            " AND refresh_token = " + txn.quote(refreshToken) + ";"
        );
        if(result.empty()){
            Json::Value err;
            err["status"] = "error";
            err["message"] = "Invalid or expired refresh token";

            txn.commit();

            auto response = drogon::HttpResponse::newHttpJsonResponse(err);
            response->setStatusCode(drogon::HttpStatusCode::k401Unauthorized); 
            
            callback(response);
            return;
        }
        txn.commit();

        validateRefreshToken(refreshToken);

        std::string token = generateAndCommitAccessToken(username);

        Json::Value resp;
        resp["status"] = "success";
        resp["message"] = "Token update successfuly";

        auto response = drogon::HttpResponse::newHttpJsonResponse(resp);
        response->addHeader("access-token", token);
        callback(response);

    }
    catch(const std::exception& e)
    {
        Json::Value err;
        err["status"] = "error";
        err["message"] = e.what();

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(drogon::HttpStatusCode::k500InternalServerError);

        if(std::string(e.what()) == "Expired token lifetime"){

            response->setStatusCode(drogon::HttpStatusCode::k401Unauthorized);
        }
        
        callback(response);
    }

}

