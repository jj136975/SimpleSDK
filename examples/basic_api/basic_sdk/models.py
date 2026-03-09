from serde import serde


@serde
class MyApiError:
    code: int
    message: str


class MyRole:
    ADMIN = "admin"
    USER = "user"


@serde
class MyProfile:
    id: int
    name: str
    role: MyRole
