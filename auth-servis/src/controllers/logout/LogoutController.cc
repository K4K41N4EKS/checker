#include "LogoutController.h"
#include "ServisConfig.h"

#include <drogon/drogon.h>
#include <jsoncpp/json/json.h>
#include <pqxx/pqxx>
#include <cstdlib>


void LogoutController::logout(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback){
    
    auto headers = (*req).getHeaders();
        
    if(headers.empty() || headers.find("refresh-token") == headers.end() || 
       headers["refresh-token"].empty()){
        
        Json::Value err;
        err["status"] = "error";
        err["message"] = "Вы не авторизованы.";

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(drogon::HttpStatusCode::k401Unauthorized);
        
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
    catch(const std::exception& e)
    {
        std::cout << e.what() << '\n';

        Json::Value err;
        err["status"] = "error";
        err["message"] = std::string("Вы не авторизованы. (такого пользователя нет - '") +
        std::string(username) + std::string("'");

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(drogon::HttpStatusCode::k401Unauthorized);
        
        callback(response);
        return;
    }
    

    try
    {
        // проверка наличия пользователя в бд и залогинен ли он
        configdb::ServisConfig servisCfg = 
            configdb::ServisConfig(std::string(getenv("AUTH_SERVIS_DB_DIR")));


        pqxx::connection conn(servisCfg.getConnectionArgs());
        
        pqxx::work txn(conn);
        auto result = txn.exec(
            "SELECT * FROM users WHERE username = " + 
            txn.quote(username) + " AND refresh_token = " +
            txn.quote(refresh_t) + ";"
        );
        if (result.empty()) {
            throw std::runtime_error("Вы не авторизованы.");
        }
        txn.commit();


        // завершение сессии польз. удалением рефреш и ацесс токенов из БД
        pqxx::work update_txn(conn);
        auto new_result = update_txn.exec(
            "UPDATE users SET access_token = '', "
            "refresh_token = '' WHERE username = " + 
            update_txn.quote(username) + " AND refresh_token = " +
            update_txn.quote(refresh_t) + ";"
        );
        if (result.empty()) {
            throw std::runtime_error("Ошибка сервиса.");
        }
        update_txn.commit();


        // отправка ответа об успешном выходе из сессии польз.
        Json::Value resp;
        resp["status"] = "success";
        resp["message"] = "Выход выполнен успешно.";

        auto response = drogon::HttpResponse::newHttpJsonResponse(resp);
        response->setStatusCode(drogon::HttpStatusCode::k201Created);

        callback(response);


    }
    catch(const std::exception& e)
    {
        std::cout << e.what() << '\n';

        Json::Value err;
        err["status"] = "error";
        err["message"] = "Вы не авторизованы.";

        auto response = drogon::HttpResponse::newHttpJsonResponse(err);
        response->setStatusCode(drogon::HttpStatusCode::k401Unauthorized);
        
        callback(response);
        return;
    }
    
    

}

