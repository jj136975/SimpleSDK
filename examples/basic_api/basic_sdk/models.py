from enum import StrEnum

from serde import serde


@serde
class MyApiError:
    code: int
    message: str


class MyRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


@serde
class MyProfile:
    id: int
    name: str
    role: MyRole
