"""Esquemas de entrada y salida de identidad. Campos desconocidos se rechazan."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.domain.legal_rules import needs_terms
from app.domain.roles import UserRole
from app.persistence.models_identity import UserAccount


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_max_length=254)


class RegisterRequest(StrictModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)
    display_name: str = Field(max_length=60)
    birth_date: date
    role: UserRole
    sports: list[str] = Field(min_length=1, max_length=10)
    city: str = Field(max_length=60)
    neighborhood: str = Field(max_length=60)
    position: str | None = Field(default=None, max_length=40)
    accept_terms: bool = False  # Sprint 27: obligatorio en la práctica; sin él responde TERMS_NOT_ACCEPTED


class LoginRequest(StrictModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


class AddRoleRequest(StrictModel):
    role: UserRole
    sports: list[str] = Field(min_length=1, max_length=10)


class UserOut(BaseModel):
    id: int
    email: str
    display_name: str
    roles: list[UserRole]
    sports: list[str]
    city: str
    neighborhood: str
    position: str | None
    needs_terms: bool = False  # Sprint 27: debe aceptar la versión vigente antes de seguir

    @classmethod
    def from_account(cls, user: UserAccount) -> "UserOut":
        return cls(
            id=user.id, email=user.email, display_name=user.display_name,
            roles=[UserRole(r.role) for r in user.roles],
            sports=sorted(s.sport_code for s in user.sports),
            city=user.city, neighborhood=user.neighborhood, position=user.position,
            needs_terms=needs_terms(user.terms_version),
        )


class SessionOut(BaseModel):
    token: str
    user: UserOut
