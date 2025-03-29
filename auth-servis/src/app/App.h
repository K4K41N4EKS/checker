#pragma once

#include <drogon/drogon.h>
#include "ServisConfig.h"
#include "auth.h"

#include <iostream>
#include <cstdlib>


namespace app{

class App{

public:
    App(){};
    int run(int argc, char* argv[]);

};

}