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

    drogon::app()
        .loadConfigFile(serverCfgPath)
        .run();

}
