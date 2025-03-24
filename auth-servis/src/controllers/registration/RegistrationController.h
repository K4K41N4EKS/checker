#pragma once

#include <drogon/HttpController.h>
#include "auth.h"



class RegistrationController : 
    public drogon::HttpController<RegistrationController>, 
    public authAndValid::IAuth {

public:
    METHOD_LIST_BEGIN

    ADD_METHOD_TO(
        RegistrationController::registration,
        "/registration",
        drogon::Post
    );
    
    METHOD_LIST_END


    void registration(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback);


};