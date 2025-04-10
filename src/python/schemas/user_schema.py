from pydantic import BaseModel

class UserTokens(BaseModel):
    """Модель для хранения access и refresh токенов"""
    access_token: str
    refresh_token: str
    
    @property
    def auth_header(self) -> dict:
        """Генерирует заголовки авторизации"""
        return {
            "Authorization": f"Bearer {self.access_token}"
        }
    
    @property
    def refresh_header(self) -> dict:
        """Генерирует заголовки авторизации"""
        return {
            "refresh-token": self.refresh_token
        }
    