#pragma once

#include <drogon/HttpController.h>
#include "auth.h"



class UpdateAssessController : 
    public drogon::HttpController<UpdateAssessController>, 
    public authAndValid::IAuth {

public:
    METHOD_LIST_BEGIN
    
    ADD_METHOD_TO(
        UpdateAssessController::updateAccessToken,
        "/updateaccesst",
        drogon::Post
    );
    
    METHOD_LIST_END

    void updateAccessToken(const drogon::HttpRequestPtr &req,
        std::function<void(const drogon::HttpResponsePtr &)> &&callback);

};