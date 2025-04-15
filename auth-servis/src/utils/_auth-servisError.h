#include <exception>
#include <string>


namespace authServisErrors{

enum class ErrorCode{

    None = 0,
    ConfigModule_CantOpenFile,
    ConfigModule_FileIsEmpty,
    AuthModule_ExpiredTokenLifetime,
    AuthModule_CantGenerateToken,
    AuthModule_UserNotFound,
    AuthModule_CantUpdateUsersTableWithAccessToken,
    AuthModule_CantUpdateUsersTableWithRefreshToken,
    AuthModule_UsernameClaimIsEmpty,
    UpdateAccessModule_EmptyRefreshToken,
    UpdateAccessModule_UnregisteredRefreshToken,
    RegistrationModule_IncompleteData,
    RegistrationModule_UsernameIsAlreadyTaken,
    RegistrationModule_CantDeleteUser,
    RegistrationModule_BadRequestToMainApplication,
    LogoutModule_EmptyRefreshToken,
    LogoutModule_UnauthorizedUser,
    LogoutModule_CantDeleteTokens,
    LoginModule_IncompleteData,
    LoginModule_IncorrectSignInData

}

const char * errorCodeToString(ErrorCode code);

class AuthServisException: std::exception{

    ErrorCode code;
    std::string message;

public:
    AuthServisException(ErrorCode _code_);
    
    ErrorCode codeValue() const noexcept;

    const char* what() const noexcept override;

}

}