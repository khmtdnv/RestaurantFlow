from api.dependencies import RedisDependency, UOWDependency, get_token_payload
from fastapi import APIRouter, Depends, Response
from schemas.auth import (
    LogoutRequestDTO,
    LogoutResponseDTO,
    RefreshRequestDTO,
    RefreshResponseDTO,
    ResendCodeRequestDTO,
    ResendCodeResponseDTO,
    SendCodeRequestDTO,
    SendCodeResponseDTO,
    VerifyCodeRequestDTO,
    VerifyCodeResponseDTO,
)
from services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/verify")
async def verify_gateway_auth(payload: dict = Depends(get_token_payload)):
    user_id = str(payload.get("sub"))
    is_superuser = str(payload.get("is_superuser"))
    return Response(status_code=200, headers={"X-User-Id": user_id, "X-Is-Superuser": is_superuser})


@router.post("/send-code", response_model=SendCodeResponseDTO)
async def send_sms_code(
    request_data: SendCodeRequestDTO,
    uow: UOWDependency,
    redis: RedisDependency,
):
    service = AuthService(uow)
    await service.send_sms_code(redis=redis, phone_number=request_data.phone_number)
    return SendCodeResponseDTO(status="success", message="Код отправлен")


@router.post("/verify-code", response_model=VerifyCodeResponseDTO)
async def verify_phone_by_code(
    request_data: VerifyCodeRequestDTO,
    uow: UOWDependency,
    redis: RedisDependency,
):
    service = AuthService(uow)
    tokens = await service.verify_phone_by_code(
        redis=redis,
        phone_number=request_data.phone_number,
        code=request_data.code,
    )
    return tokens


@router.post("/resend-code", response_model=ResendCodeResponseDTO)
async def resend_sms_code(
    request_data: ResendCodeRequestDTO,
    uow: UOWDependency,
    redis: RedisDependency,
):
    service = AuthService(uow)
    await service.resend_sms_code(redis=redis, phone_number=request_data.phone_number)
    return ResendCodeResponseDTO(status="success", message="Код отправлен")


@router.post("/refresh", response_model=RefreshResponseDTO)
async def refresh_token_pair(
    request_data: RefreshRequestDTO,
    uow: UOWDependency,
):
    service = AuthService(uow)
    tokens = await service.refresh_token_pair(refresh_token=request_data.refresh_token)
    return tokens


@router.post("/logout", response_model=LogoutResponseDTO)
async def logout(
    request_data: LogoutRequestDTO,
    uow: UOWDependency,
    redis: RedisDependency,
):
    service = AuthService(uow)
    await service.logout(redis=redis, refresh_token=request_data.refresh_token)
    return LogoutResponseDTO(status="success", message="Вы разлогинены")
