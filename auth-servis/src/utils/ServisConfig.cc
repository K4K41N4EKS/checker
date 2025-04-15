#include "ServisConfig.h"
#include <string>
#include <iostream>
#include <fstream>
#include <jsoncpp/json/json.h>
#include <cstdlib>
#include "_auth-servisError.h"




configdb::ServisConfig::ServisConfig(const std::string& path){

    Json::Value data;
    
    std::ifstream file(
        path,
        std::ifstream::binary);
    if(!file.is_open()){

        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::ConfigModule_CantOpenFile
        );
    }

    file >> data;

    file.close();
    
    if(data.empty()){
        throw authServisErrors::AuthServisException(
            authServisErrors::ErrorCode::ConfigModule_FileIsEmpty
        );
    }

    configPath = path;
    dbhost = data["dbhost"].asString();
    dbname = data["dbname"].asString();
    dbuser = data["dbuser"].asString();
    dbpasswd = data["dbpasswd"].asString();
    dbport = data["dbport"].asInt();

    secret = data["secret"].asString();
    checker_secret = data["checker_secret"].asString();

    access_t_lifestyle_time_hours = data["access-t-lifestyle-time-hours"].asInt();
    access_t_lifestyle_time_minuts = data["access-t-lifestyle-time-minuts"].asInt();
    refresh_t_lifestyle_time_hours = data["refresh-t-lifestyle-time-hours"].asInt();
    refresh_t_lifestyle_time_minuts = data["refresh-t-lifestyle-time-minuts"].asInt();

}

std::string configdb::ServisConfig::getConnectionArgs(){

    return "host=" + dbhost +
           " port=" + std::to_string(dbport) +
           " dbname=" + dbname +
           " user=" + dbuser +
           " password=" + dbpasswd;

}

std::string configdb::ServisConfig::getSecretKey(){

    return secret;

}

std::string configdb::ServisConfig::getCheckerAppSecret(){

    return checker_secret;

}

int configdb::ServisConfig::getAccessTLifestyleTime_hours(){
    
    return access_t_lifestyle_time_hours;

}

int configdb::ServisConfig::getAccessTLifestyleTime_minuts(){

    return access_t_lifestyle_time_minuts;

}

int configdb::ServisConfig::getRefreshTLifestyleTime_hours(){

    return refresh_t_lifestyle_time_hours;

}

int configdb::ServisConfig::getRefreshTLifestyleTime_minuts(){
    
    return refresh_t_lifestyle_time_minuts;

}