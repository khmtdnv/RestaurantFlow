from pydantic import BaseModel


class SendCodeRequestDTO(BaseModel):
    phone_number: str


class SendCodeResponseDTO(BaseModel):
    status: str
    message: str


class VerifyCodeRequestDTO(BaseModel):
    phone_number: str
    code: str


class VerifyCodeResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class ResendCodeRequestDTO(SendCodeRequestDTO):
    pass


class ResendCodeResponseDTO(SendCodeResponseDTO):
    pass


class RefreshRequestDTO(BaseModel):
    refresh_token: str


class RefreshResponseDTO(VerifyCodeResponseDTO):
    pass


class LogoutRequestDTO(RefreshRequestDTO):
    pass


class LogoutResponseDTO(SendCodeResponseDTO):
    pass
