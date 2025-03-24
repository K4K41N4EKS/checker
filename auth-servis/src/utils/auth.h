#pragma once

#include <pqxx/pqxx>
#include <drogon/drogon.h>
#include <jwt-cpp/jwt.h>
#include "ServisConfig.h"
#include <cstdlib>


namespace authAndValid{

class IAuth{

private:
    std::string GenerateJwt(const std::string &username,
        const int &hours,
        const int &minutes);
    

public:
    void validateRefreshToken(std::string &token);
    
    std::string generateAndCommitAccessToken(const std::string &username);

    std::string generateAndCommitRefreshToken(const std::string &username);

    std::string getUsernameFromToken(std::string token);

};

}