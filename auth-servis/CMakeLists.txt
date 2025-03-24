cmake_minimum_required(VERSION 3.5)
project(auth-servis CXX)


set(CMAKE_CXX_STANDARD 17)

set(SRC_FILES
    main.cc
    src/app/App.cc
    src/controllers/login/LoginController.cc
    src/controllers/logout/LogoutController.cc
    src/controllers/registration/RegistrationController.cc
    src/controllers/updateaccess/UpdateAssessController.cc
    src/utils/auth.cc
    src/utils/ServisConfig.cc
)


aux_source_directory(controllers CTL_SRC_DIR)


include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/src/app
    ${CMAKE_CURRENT_SOURCE_DIR}/src/controllers/login
    ${CMAKE_CURRENT_SOURCE_DIR}/src/controllers/logout
    ${CMAKE_CURRENT_SOURCE_DIR}/src/controllers/registration
    ${CMAKE_CURRENT_SOURCE_DIR}/src/controllers/updateaccess
    ${CMAKE_CURRENT_SOURCE_DIR}/src/utils
)


add_executable(${PROJECT_NAME} ${SRC_FILES} ${CTL_SRC_DIR})


add_subdirectory(External/jwt)


# find jwt
target_include_directories(${PROJECT_NAME} PUBLIC External/jwt/include)
target_link_libraries(${PROJECT_NAME} PUBLIC jwt-cpp::jwt-cpp)


# Find Drogon
find_package(Drogon CONFIG REQUIRED)

# Find PostgreSQL
find_package(PostgreSQL REQUIRED)

# Specify the path to libpqxx
set(PQXX_DIR "/usr/local/lib/cmake/libpqxx")
find_package(libpqxx REQUIRED)

set(cpr_DIR "/usr/local/lib/cmake/cpr")
find_package(cpr REQUIRED)


# Link libraries
target_link_libraries(${PROJECT_NAME} PRIVATE 
    cpr::cpr
    Drogon::Drogon 
    libpqxx::pqxx
    ${PostgreSQL_LIBRARIES}
)


set(CPACK_PACKAGE_NAME ${PROJECT_NAME})
set(CPACK_DEBIAN_PACKAGE_MAINTAINER DM)
set(CPACK_GENERATOR "DEB")
set(CPACK_PACKAGE_HOMEPAGE_URL https://github.com/dipsomask/auth-servis.git)
set(CPACK_DEBIAN_PACKAGE_ARCHITECTURE "amd64")
set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
install(TARGETS ${PROJECT_NAME} DESTINATION /usr/bin)

include(CPack)
