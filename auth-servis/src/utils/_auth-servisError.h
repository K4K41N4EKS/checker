#include <exception>
#include <string>
#include <drogon/drogon.h>


namespace authServisErrors{

enum class ErrorCode{

    None = 0,

    // http 400
    RegistrationModule_IncompleteData,
    RegistrationModule_UsernameIsAlreadyTaken,
    LoginModule_IncompleteData,
    LoginModule_IncorrectSignInData,

    // http 401
    UpdateAccessModule_EmptyRefreshToken,
    UpdateAccessModule_UnregisteredRefreshToken,
    LogoutModule_EmptyRefreshToken,
    LogoutModule_UnauthorizedUser,

    // http 409
    AuthModule_CantUpdateUsersTableWithAccessToken,
    AuthModule_CantUpdateUsersTableWithRefreshToken,
    AuthModule_UsernameClaimIsEmpty,
    RegistrationModule_CantDeleteUser,
    RegistrationModule_BadRequestToMainApplication,
    LogoutModule_CantDeleteTokens,

    // http 500
    ConfigModule_CantOpenFile,
    ConfigModule_FileIsEmpty,
    AuthModule_ExpiredTokenLifetime,
    AuthModule_CantGenerateToken,
    AuthModule_UserNotFound

}

const char * errorCodeToString(ErrorCode code);

class AuthServisException: std::exception{

    ErrorCode code;
    std::string message;

public:
    AuthServisException(ErrorCode _code_);
    
    ErrorCode codeValue() const noexcept;

    const char* what() const noexcept override;

    drogon::HttpStatusCode ToDrogonHttpErrorCode();

}

}