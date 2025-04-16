#include "_auth-servisError.h"

const char * authServisErrors::errorCodeToString(ErrorCode code){

    switch (code)
    {
    case ErrorCode::None: 
        return "Отсутствует ошибка.";
    case ErrorCode::ConfigModule_CantOpenFile: 
        return "Не удалось открыть файл.";
    case ErrorCode::ConfigModule_FileIsEmpty: 
        return "Файл пуст.";
    case ErrorCode::AuthModule_ExpiredTokenLifetime: 
        return "Время жизни токена истекло.";
    case ErrorCode::AuthModule_CantGenerateToken: 
        return "Ошибка генерации токена.";
    case ErrorCode::AuthModule_UserNotFound: 
        return "Пользователь не найден.";
    case ErrorCode::AuthModule_CantUpdateUsersTableWithAccessToken: 
        return "Ошибка добавления Access Token для пользователя.";
    case ErrorCode::AuthModule_CantUpdateUsersTableWithRefreshToken: 
        return "Ошибка добавления Refresh Token для пользователя.";
    case ErrorCode::AuthModule_UsernameClaimIsEmpty: 
        return "В полезной нагрузке токена отсутствует имя пользователя.";
    case ErrorCode::UpdateAccessModule_EmptyRefreshToken: 
        return "Отсутствует Refresh Token.";
    case ErrorCode::UpdateAccessModule_UnregisteredRefreshToken: 
        return "Refresh Token не зарегистрирован.";
    case ErrorCode::RegistrationModule_IncompleteData: 
        return "Заполнены не все поля для регистрации.";
    case ErrorCode::RegistrationModule_UsernameIsAlreadyTaken: 
        return "Имя пользователя уже занято, попробуйте другое.";
    case ErrorCode::RegistrationModule_CantDeleteUser: 
        return "Ошибка удаления пользователя при неудачной связи с приложением.";
    case ErrorCode::RegistrationModule_BadRequestToMainApplication: 
        return "Ошибка сервиса, не удаётся связаться с приложением.";
    case ErrorCode::LogoutModule_EmptyRefreshToken: 
        return "Отсутствует Refresh Token.";
    case ErrorCode::LogoutModule_UnauthorizedUser: 
        return "Вы не авторизованы.";
    case ErrorCode::LogoutModule_CantDeleteTokens: 
        return "Ошибка при удалении токенов.";
    case ErrorCode::LoginModule_IncompleteData: 
        return "Заполните все поля для входа.";
    case ErrorCode::LoginModule_IncorrectSignInData: 
        return "Неверные данные для входа.";
    
    default: return "Неизвестная ошибка.";
    }

}

authServisErrors::AuthServisException::AuthServisException(ErrorCode _code_){

    code = _code_;
    message = std::string(authServisErrors::errorCodeToString(_code_));

}

authServisErrors::ErrorCode authServisErrors::AuthServisException::codeValue() const{

    return code;

}

const char* authServisErrors::AuthServisException::what() const{

    return message.c_str();

}

drogon::HttpStatusCode authServisErrors::AuthServisException::ToDrogonHttpErrorCode(){

    if(code > 0 && code < 5){

        return drogon::HttpStatusCode::k400BadRequest;
    
    }
    else if(code > 4 && code < 9){

        return drogon::HttpStatusCode::k401Unauthorized;

    }
    else if(code > 8 && code < 15){

        return drogon::HttpStatusCode::k409Conflict;

    }
    else{

        return drogon::HttpStatusCode::k500InternalServerError;

    }
    
}
