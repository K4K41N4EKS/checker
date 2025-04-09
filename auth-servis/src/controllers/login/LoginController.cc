#include "LoginController.h"
#include "ServisConfig.h"

#include <drogon/drogon.h>
#include <jsoncpp/json/json.h>
#include <pqxx/pqxx>
#include <cstdlib>


void LoginController::login(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback){
    
    auto headers = (*req).getHeaders();
        
    if(headers.empty() || headers.find("username") == headers.end() || 
    headers.find("passwd") == headers.end() || 
    headers["username"].empty() || headers["passwd"].empty()){
        
        Json::Value err;
        err["status"] = "error";
        err["message"] = "Invalid username or password";

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(drogon::HttpStatusCode::k400BadRequest);
        
        callback(response);
        return;

    }

    std::string username = headers["username"];
    std::string passwd = headers["passwd"];
    std::cout << "\n" << drogon::utils::getSha256(passwd) << "\n";

    try{


        configdb::ServisConfig servisCfg = 
            configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));


        pqxx::connection conn(servisCfg.getConnectionArgs());
        pqxx::work txn(conn);

        auto result = txn.exec(
            "SELECT * FROM users WHERE username = " + 
            txn.quote(username) + " AND password_hash = " +
            txn.quote(drogon::utils::getSha256(passwd)) + ";"
        );
        if (result.empty()) {
            txn.commit();
            throw std::runtime_error("Unexpected result from Select query");
        }
        txn.commit();

        std::string refreshToken = generateAndCommitRefreshToken(username);
        std::string accessToken = generateAndCommitAccessToken(username);

        Json::Value resp;
        resp["status"] = "success";
        resp["message"] = "User successfully logined";

        auto response = drogon::HttpResponse::newHttpJsonResponse(resp);
        response->setStatusCode(drogon::HttpStatusCode::k200OK);
        response->addHeader("refresh-token", refreshToken);
        response->addHeader("access-token", accessToken);

        callback(response);

    }
    catch(const std::exception& e){
        
        Json::Value err;
        err["status"] = "error";
        err["message"] = e.what();

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(drogon::HttpStatusCode::k500InternalServerError);
        
        callback(response);

    }
    

}

