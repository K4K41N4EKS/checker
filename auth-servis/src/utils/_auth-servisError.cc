#include "_auth-servisError.h"

const char * authServisErrors::errorCodeToString(ErrorCode code){

    switch (code)
    {
    case ErrorCode::None: 
        return "Отсутствует ошибка.";
        break;
    case ErrorCode::ConfigModule_CantOpenFile: 
        return "Не удалось открыть файл.";
        break;
    case ErrorCode::ConfigModule_FileIsEmpty: 
        return "Файл пуст.";
        break;
    case ErrorCode::AuthModule_ExpiredTokenLifetime: 
        return "Время жизни токена истекло.";
        break;
    case ErrorCode::AuthModule_CantGenerateToken: 
        return "Ошибка генерации токена.";
        break;
    case ErrorCode::AuthModule_UserNotFound: 
        return "Пользователь не найден.";
        break;
    case ErrorCode::AuthModule_CantUpdateUsersTableWithAccessToken: 
        return "Ошибка добавления Access Token для пользователя.";
        break;
    case ErrorCode::AuthModule_CantUpdateUsersTableWithRefreshToken: 
        return "Ошибка добавления Refresh Token для пользователя.";
        break;
    case ErrorCode::AuthModule_UsernameClaimIsEmpty: 
        return "В полезной нагрузке токена отсутствует имя пользователя.";
        break;
    case ErrorCode::UpdateAccessModule_EmptyRefreshToken: 
        return "Отсутствует Refresh Token.";
        break;
    case ErrorCode::UpdateAccessModule_UnregisteredRefreshToken: 
        return "Refresh Token не зарегистрирован.";
        break;
    case ErrorCode::RegistrationModule_IncompleteData: 
        return "Заполнены не все поля для регистрации.";
        break;
    case ErrorCode::RegistrationModule_UsernameIsAlreadyTaken: 
        return "Имя пользователя уже занято, попробуйте другое.";
        break;
    case ErrorCode::RegistrationModule_CantDeleteUser: 
        return "Ошибка удаления пользователя при неудачной связи с приложением.";
        break;
    case ErrorCode::RegistrationModule_BadRequestToMainApplication: 
        return "Ошибка сервиса, не удаётся связаться с приложением.";
        break;
    case ErrorCode::LogoutModule_EmptyRefreshToken: 
        return "Отсутствует Refresh Token.";
        break;
    case ErrorCode::LogoutModule_UnauthorizedUser: 
        return "Вы не авторизованы.";
        break;
    case ErrorCode::LogoutModule_CantDeleteTokens: 
        return "Ошибка при удалении токенов.";
        break;
    case ErrorCode::LoginModule_IncompleteData: 
        return "Заполните все поля для входа.";
        break;
    case ErrorCode::LoginModule_IncorrectSignInData: 
        return "Неверные данные для входа.";
        break;
    
    default: "Неизвестная ошибка."; break;
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


