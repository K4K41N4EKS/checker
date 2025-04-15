#include "RegistrationController.h"
#include "ServisConfig.h"
#include "_auth-servisError.h"

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
    catch(const std::exception& e)
    {
        Json::Value err;
        err["status"] = "error";
        err["message"] = e.what();

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(drogon::HttpStatusCode::k409Conflict);
        
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
        pqxx::work addNewStringToUsersTable_Txn(conn);

        auto result = addNewStringToUsersTable_Txn.exec(
            "INSERT INTO users (user_id, username, password_hash) VALUES (" + 
            addNewStringToUsersTable_Txn.quote(user_id) + ", " +
            addNewStringToUsersTable_Txn.quote(username) + ", " +
            addNewStringToUsersTable_Txn.quote(drogon::utils::getSha256(passwd)) + ")"
        );
        if (!result.empty()) {
            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::RegistrationModule_UsernameIsAlreadyTaken
            );
        }
        addNewStringToUsersTable_Txn.commit();

        
        
        cpr::Response resp = cpr::Post(
            cpr::Url{"http://checker_backend:3000/create_user"},
            cpr::Header{
                {"X-Internal-Secret", servisCfg.getCheckerAppSecret()}, 
                {"user_id", user_id}, 
                {"username", username}}
        );
        if(resp.status_code != 201){
            
            pqxx::connection conn(servisCfg.getConnectionArgs());
            pqxx::work deleteLastAddedStringToUsersTable_Txn(conn);

            auto result = deleteLastAddedStringToUsersTable_Txn.exec(
                "DELETE FROM users WHERE user_id = " + 
                deleteLastAddedStringToUsersTable_Txn.quote(user_id) + ";"
            );
            if (!result.empty()) {
                throw authServisErrors::AuthServisException(
                    authServisErrors::ErrorCode::RegistrationModule_CantDeleteUser
                );
            }
            deleteLastAddedStringToUsersTable_Txn.commit();

            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::RegistrationModule_BadRequestToMainApplication
            );
        }



        Json::Value ans;
        ans["status"] = "success";
        ans["message"] = "Регистрация прошла успешно.";

        auto response = drogon::HttpResponse::newHttpJsonResponse(ans);
        response->setStatusCode(drogon::HttpStatusCode::k200OK);
        
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

