"""Models used for API request and response validation."""

from pydantic import BaseModel


class AuthReq(BaseModel):
    """The request format for the authorization API request."""

    email: str
    password: str


class AccountReq(BaseModel):
    """The request format for account API request."""

    password: str


class MessageReq(BaseModel):
    """The request format for the contact message API request."""

    category: str = ""
    first: str
    last: str
    message: str


class BaseResp(BaseModel):
    """General API response parameters."""

    status: str
    message: str


class AuthResp(BaseResp):
    """Response parameters for the authorization API."""

    token: str
