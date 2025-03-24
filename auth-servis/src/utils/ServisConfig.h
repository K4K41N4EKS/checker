#pragma once

#include <string>
#include <jsoncpp/json/json.h>


namespace configdb {


    class ServisConfig {
        private:
            std::string configPath;
            std::string dbhost;
            std::string dbname;
            std::string dbuser;
            std::string dbpasswd;
            int dbport;

            std::string secret;
        
            int access_t_lifestyle_time_hours;
            int access_t_lifestyle_time_minuts;
            int refresh_t_lifestyle_time_hours;
            int refresh_t_lifestyle_time_minuts;

        public:
            ServisConfig(){};
            ServisConfig(const std::string& configPath);      

            std::string getConnectionArgs();
            std::string getSecretKey();

            int getAccessTLifestyleTime_hours();
            int getAccessTLifestyleTime_minuts();
            int getRefreshTLifestyleTime_hours();
            int getRefreshTLifestyleTime_minuts();
    };


}
