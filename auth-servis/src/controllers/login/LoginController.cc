#include "LoginController.h"
#include "ServisConfig.h"
#include "_database.h"

#include <drogon/drogon.h>
#include <jsoncpp/json/json.h>
#include <pqxx/pqxx>
#include <cstdlib>


void LoginController::login(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback){
    
    auto headers = (*req).getHeaders();
        
    try
    {
        if(headers.empty() || 
            headers.find("username") == headers.end() || 
            headers.find("passwd") == headers.end() || 
            headers["username"].empty() || headers["passwd"].empty() ||
            headers["username"] == "" || headers["passwd"] == ""){
        
            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::LoginModule_IncompleteData
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
    

    std::string username = headers["username"];
    std::string passwd = headers["passwd"];

    try{


        _database::database db;
        db.q_login_select(username, passwd);

        std::string refreshToken = generateAndCommitRefreshToken(username);
        std::string accessToken = generateAndCommitAccessToken(username);

        Json::Value resp;
        resp["status"] = "success";
        resp["message"] = "Вход выполнен успешно.";

        auto response = drogon::HttpResponse::newHttpJsonResponse(resp);
        response->setStatusCode(drogon::HttpStatusCode::k201Created);
        response->addHeader("refresh-token", refreshToken);
        response->addHeader("access-token", accessToken);

        callback(response);

    }
    catch(const authServisErrors::AuthServisException& e){
        
        Json::Value err;
        err["status"] = "error";
        err["message"] = e.what();

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(e.ToDrogonHttpErrorCode());
        
        callback(response);

    }
    

}

