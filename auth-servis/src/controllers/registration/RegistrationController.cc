#include "RegistrationController.h"
#include "ServisConfig.h"
#include "_database.h"

#include <drogon/drogon.h>
#include <jsoncpp/json/json.h>
#include <pqxx/pqxx>
#include <cstdlib>
#include <cpr/cpr.h>



void RegistrationController::registration(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback){

    auto headers = (*req).getHeaders();

    try
    {
        if(headers.empty() || headers.find("username") == headers.end() || 
            headers.find("passwd") == headers.end() || 
            headers["username"].empty() || headers["passwd"].empty() ||
            headers["username"] == "" || headers["passwd"] == ""){
            
            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::RegistrationModule_IncompleteData
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
    std::string user_id = drogon::utils::getUuid();

    try{


        configdb::ServisConfig servisCfg = 
            configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));


        _database::database db;
        db.q_registration_insert(user_id, username, passwd);
        
        
        cpr::Response resp = cpr::Post(
            cpr::Url{"http://checker_backend:3000/create_user"},
            cpr::Header{
                {"X-Internal-Secret", servisCfg.getCheckerAppSecret()}, 
                {"user_id", user_id}, 
                {"username", username}}
        );
        if(resp.status_code != 201){
            
            _database::database db;
            db.q_registration_delete(user_id);

            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::RegistrationModule_BadRequestToMainApplication
            );
        }



        Json::Value ans;
        ans["status"] = "success";
        ans["message"] = "Регистрация прошла успешно.";

        auto response = drogon::HttpResponse::newHttpJsonResponse(ans);
        response->setStatusCode(drogon::HttpStatusCode::k201Created);
        
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

