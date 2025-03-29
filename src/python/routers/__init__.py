from .auth_registration_router import router as auth_router
from .file_router import router as file_router
from .template_router import router as template_router

all_routers = [file_router, auth_router, template_router]
