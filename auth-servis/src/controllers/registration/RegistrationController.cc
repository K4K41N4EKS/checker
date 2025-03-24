#include "RegistrationController.h"
#include "ServisConfig.h"

#include <drogon/drogon.h>
#include <jsoncpp/json/json.h>
#include <pqxx/pqxx>
#include <cstdlib>



void RegistrationController::registration(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback){

    auto headers = (*req).getHeaders();

    if(headers.empty() || headers.find("username") == headers.end() || 
        headers.find("passwd") == headers.end() || 
        headers["username"].empty() || headers["passwd"].empty()){
        
        Json::Value err;
        err["status"] = "error";
        err["message"] = "Invalid headers";

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(drogon::HttpStatusCode::k400BadRequest);
        
        callback(response);
        return;

    }

    std::string username = headers["username"];
    std::string passwd = headers["passwd"];

    try{


        configdb::ServisConfig servisCfg = 
            configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));


        pqxx::connection conn(servisCfg.getConnectionArgs());
        pqxx::work txn(conn);

        auto result = txn.exec(
            "INSERT INTO users (username, password_hash) VALUES (" + 
            txn.quote(username) + ", " +
            txn.quote(drogon::utils::getSha256(passwd)) + ")"
        );
        if (!result.empty()) {
            throw std::runtime_error("Unexpected result from INSERT query");
        }
        txn.commit();

        Json::Value resp;
        resp["status"] = "success";
        resp["message"] = "User registred successfully";

        auto response = drogon::HttpResponse::newHttpJsonResponse(resp);
        response->setStatusCode(drogon::HttpStatusCode::k200OK);
        
        callback(response);

    }
    catch(const std::exception& e){
        
        Json::Value err;
        err["status"] = "error";
        err["error"] = e.what();

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(drogon::HttpStatusCode::k500InternalServerError);
        
        callback(response);

    }
    
}

