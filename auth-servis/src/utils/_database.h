#include "ServisConfig.h"
#include "_auth-servisError.h"

#include <string.h>
#include <pqxx/pqxx>
#include <cstdlib>

namespace _database {

class database {

std::string connectionArguments;

public:
    database();

    void q_registration_insert(std::string userid, std::string username, std::string password);
    void q_registration_delete(std::string userid);
    void q_updateaccess_select_username_and_refresh(std::string username, std::string refreshToken);
    void q_logout_select_username_and_refresh(std::string username, std::string refreshToken);
    void q_logout_update(std::string username, std::string refreshToken);
    void q_login_select(std::string username, std::string password);

};

}