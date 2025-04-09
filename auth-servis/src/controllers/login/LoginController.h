#pragma once

#include <drogon/HttpController.h>
#include "auth.h"



class LoginController : 
    public drogon::HttpController<LoginController>, 
    public authAndValid::IAuth {

public:
    METHOD_LIST_BEGIN

    ADD_METHOD_TO(
        LoginController::login,
        "/login",
        drogon::Get
    );
    
    METHOD_LIST_END


    void login(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback);


};