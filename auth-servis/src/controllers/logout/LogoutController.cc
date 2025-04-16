#include "LogoutController.h"
#include "ServisConfig.h"
#include "_auth-servisError.h"

#include <drogon/drogon.h>
#include <jsoncpp/json/json.h>
#include <pqxx/pqxx>
#include <cstdlib>


void LogoutController::logout(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback){
    
    auto headers = (*req).getHeaders();
        
    try
    {
        if(headers.empty() || 
            headers.find("refresh-token") == headers.end() || 
            headers["refresh-token"].empty() || 
            headers["refresh-token"] == ""){
            
            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::LogoutModule_EmptyRefreshToken
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
    

    std::string refresh_t = headers["refresh-token"];
    std::string username;

    try
    {
        //проверка - декодируется ли токен и получение имени пользователя из токена
        validateRefreshToken(refresh_t);

        username = getUsernameFromToken(refresh_t);

    }
    catch(const authServisErrors::AuthServisException& e){

        Json::Value err;
        err["status"] = "error";
        err["message"] = e.what();

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(e.ToDrogonHttpErrorCode());
        
        callback(response);
        return;
    }
    

    try
    {
        // проверка наличия пользователя в бд и залогинен ли он
        configdb::ServisConfig servisCfg = 
            configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));


        pqxx::connection conn(servisCfg.getConnectionArgs());
        
        pqxx::work userExistenceAndLoginedCheck_Txn(conn);
        auto result = userExistenceAndLoginedCheck_Txn.exec(
            "SELECT * FROM users WHERE username = " + 
            userExistenceAndLoginedCheck_Txn.quote(username) + 
            " AND refresh_token = " +
            userExistenceAndLoginedCheck_Txn.quote(refresh_t) + ";"
        );
        if (result.empty()) {
            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::LogoutModule_UnauthorizedUser
            );
        }
        userExistenceAndLoginedCheck_Txn.commit();


        // завершение сессии польз. удалением рефреш и ацесс токенов из БД
        pqxx::work update_txn(conn);
        auto new_result = update_txn.exec(
            "UPDATE users SET access_token = '', "
            "refresh_token = '' WHERE username = " + 
            update_txn.quote(username) + " AND refresh_token = " +
            update_txn.quote(refresh_t) + ";"
        );
        if (result.empty()) {
            throw authServisErrors::AuthServisException(
                authServisErrors::ErrorCode::LogoutModule_CantDeleteTokens
            );
        }
        update_txn.commit();


        // отправка ответа об успешном выходе из сессии польз.
        Json::Value resp;
        resp["status"] = "success";
        resp["message"] = "Выход выполнен успешно.";

        auto response = drogon::HttpResponse::newHttpJsonResponse(resp);
        response->setStatusCode(drogon::HttpStatusCode::k205ResetContent);

        callback(response);


    }
    catch(const authServisErrors::AuthServisException& e)
    {
        std::cout << e.what() << '\n';

        Json::Value err;
        err["status"] = "error";
        err["message"] = e.what();

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(e.ToDrogonHttpErrorCode());
        
        callback(response);
        return;
    }
    
    

}

