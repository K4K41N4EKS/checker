#pragma once

#include <drogon/HttpController.h>
#include "auth.h"



class LogoutController : 
    public drogon::HttpController<LogoutController>, 
    public authAndValid::IAuth {

public:
    METHOD_LIST_BEGIN

    ADD_METHOD_TO(
        LogoutController::logout,
        "/logout",
        drogon::Post
    );
    
    METHOD_LIST_END


    void logout(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback);


};