from pydantic import BaseModel, HttpUrl, Field, EmailStr, field_validator

RESERVED_PATHS={
    "api",
    "auth",
    "docs",
    "redoc",
    "openapi",
    "admin",
    "login",
    "logout",
    "register"
}

class LinkCreate(BaseModel):
    given_url: HttpUrl
    custom_slug: str | None = Field(
        default = None,
        min_length = 3,
        max_length = 20, 
        pattern = r"^[a-z0-9_]+$"
    )

class LinkResponse(BaseModel):
    given_url : str
    short_url : str
    short_code : str

class UserCreate(BaseModel):
    email : EmailStr
    username : str = Field(
        min_length = 3, 
        max_length = 20, 
        pattern=r"^[a-z0-9_]+$"
    )
    password : str = Field(
        min_length = 8,
        max_length = 128
    )
    @field_validator("username")
    @classmethod
    def prevent_reserved_username(cls, username: str) -> str:
        if username in RESERVED_PATHS:
            raise ValueError("This username is reserved.")

class LoginCred(BaseModel):
    email: EmailStr
    password : str = Field(
        min_length = 8,
        max_length = 128
    )