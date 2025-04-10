#include "App.h"
#include "ServisConfig.h"
#include "auth.h"

#include <drogon/drogon.h>
#include <iostream>
#include <cstdlib>

int app::App::run(int argc, char* argv[]){

    if(argc != 3){
        
        std::cout << "error\n   What(): invalid command args\n" <<
                     "   Correct args: cmd command [/path/to/servis/binary/file" <<
                     " /absolute/path/to/config/file/for/drogon/settings" <<
                     " /absolute/path/to/servis/config/file]\n";
        return 1;
    }


    std::string serverCfgPath = argv[1];


    std::string servisCfgPath = argv[2];
    try
    {
        setenv("AUTH_SERVIS_DB_DIR", servisCfgPath.c_str(), 1);
    }
    catch(const std::exception& e)
    {
        std::cout << "error\n   What(): " << e.what() << '\n';
        return 2;
    }

    drogon::app().registerPreRoutingAdvice(
        [](const drogon::HttpRequestPtr& req,
           drogon::AdviceCallback&& callback,
           drogon::AdviceChainCallback&& chainCallback){
            
            auto resp = drogon::HttpResponse::newHttpResponse();
            resp->addHeader(
                "Access-Control-Allow-Origin", 
                "*"
            );
            resp->addHeader(
                "Access-Control-Allow-Methods", 
                "POST, GET, OPTIONS"
            );
            resp->addHeader(
                "Access-Control-Allow-Headers", 
                "Content-Type, username, passwd, refresh-token, access-token"
            );
            resp->addHeader(
                "Access-Control-Expose-Headers", 
                "access-token, refresh-token"
            );

            if (req->method() == drogon::HttpMethod::Options) {
                resp->setStatusCode(drogon::HttpStatusCode::k200OK);
                callback(resp); // Прерываем цепочку обработки
            } else {
                chainCallback(); // Продолжаем обработку
            }
        }
    );

    drogon::app().registerPostHandlingAdvice(
        [](const drogon::HttpRequestPtr &req, const drogon::HttpResponsePtr &resp) {
            
            resp->addHeader(
                "Access-Control-Allow-Origin", 
                "*"
            );
            resp->addHeader(
                "Access-Control-Allow-Methods", 
                "POST, GET, OPTIONS"
            );
            resp->addHeader(
                "Access-Control-Allow-Headers", 
                "Content-Type, username, passwd, refresh-token, access-token"
            );
            resp->addHeader(
                "Access-Control-Expose-Headers", 
                "access-token, refresh-token"
            );
            
        });


    drogon::app()
        .loadConfigFile(serverCfgPath)
        .run();

}
