#include "RegistrationController.h"
#include "ServisConfig.h"

#include <drogon/drogon.h>
#include <jsoncpp/json/json.h>
#include <pqxx/pqxx>
#include <cstdlib>
#include <cpr/cpr.h>



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
    std::string user_id = drogon::utils::getUuid();

    try{


        configdb::ServisConfig servisCfg = 
            configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));


        pqxx::connection conn(servisCfg.getConnectionArgs());
        pqxx::work txn(conn);

        auto result = txn.exec(
            "INSERT INTO users (user_id, username, password_hash) VALUES (" + 
            txn.quote(user_id) + ", " +
            txn.quote(username) + ", " +
            txn.quote(drogon::utils::getSha256(passwd)) + ")"
        );
        if (!result.empty()) {
            throw std::runtime_error("Unexpected result from INSERT query");
        }
        txn.commit();

        
        
        cpr::Response resp = cpr::Post(
            cpr::Url{"http://checker_backend:3000/create_user"},
            cpr::Header{
                {"X-Internal-Secret", servisCfg.getCheckerAppSecret()}, 
                {"user_id", user_id}, 
                {"username", username}}
        );
        if(resp.status_code != 201){
            
            pqxx::connection conn(servisCfg.getConnectionArgs());
            pqxx::work txn(conn);

            auto result = txn.exec(
                "DELETE FROM users WHERE user_id = " + 
                txn.quote(user_id) + ";"
            );
            if (!result.empty()) {
                throw std::runtime_error("Unexpected result from DELETE query");
            }
            txn.commit();

            throw std::runtime_error(
                std::string("Main servis return status code ") + 
                std::to_string(resp.status_code) + 
                std::string(". With message: ") + 
                resp.text
            );
        }



        Json::Value ans;
        ans["status"] = "success";
        ans["message"] = "User registred successfully";

        auto response = drogon::HttpResponse::newHttpJsonResponse(ans);
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

