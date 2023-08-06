from typing import Any, Optional
from pydantic import BaseModel

class TokenResponse(BaseModel):
  access_token: str
  token_type: str
  expires_in: int
  refresh_token: Optional[str] = None
  id_token: Optional[str] = None

class UserIdentity(BaseModel):
  userId: str
  details: Optional[dict[str, Any]] = None

class UserInfoResponse(BaseModel):
  sub: str
  name: Optional[str] = None
  username: Optional[str] = None
  picture: Optional[str] = None
  email: Optional[str] = None
  email_verified: Optional[bool] = None
  phone_number: Optional[str] = None
  phone_number_verified: Optional[bool] = None
  custom_data: Any = None
  identities: Optional[dict[str, UserIdentity]] = None
