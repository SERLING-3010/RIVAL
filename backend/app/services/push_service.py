"""Notificaciones push (Sprint 24): registrar teléfonos y juntar los avisos nuevos.

Los avisos salen de los «Pendientes» que ya calcula el backend: cada ronda se avisa una sola vez por
cada pendiente nuevo. Al registrar un teléfono, lo que ya estaba pendiente no se avisa (se marca
como visto), para no llenar la pantalla de golpe. El envío a Expo lo hace `app.tools.push_worker`,
fuera de la transacción.
"""

from dataclasses import dataclass

from sqlalchemy import delete, func, select

from app.domain import push_rules
from app.domain.errors import ConflictError
from app.persistence.models_identity import UserAccount
from app.persistence.models_push import PushDevice, PushSent
from app.services import pending_service
from app.services.context import ServiceContext


@dataclass(frozen=True)
class Outgoing:
    user_id: int
    tokens: list[str]
    body: str


def _keys(ctx: ServiceContext, user: UserAccount) -> list[tuple[str, str]]:
    return [(push_rules.item_key(i.kind, i.target_id), i.kind) for i in pending_service.pending(ctx, user)]


def _mark(ctx: ServiceContext, user_id: int, keys: list[str]) -> None:
    now = ctx.clock.now()
    for key in keys:
        ctx.db.add(PushSent(user_id=user_id, item_key=key, sent_at=now))
    ctx.db.flush()


def _sent(ctx: ServiceContext, user_id: int) -> set[str]:
    return set(ctx.db.scalars(select(PushSent.item_key).where(PushSent.user_id == user_id)))


def register(ctx: ServiceContext, actor: UserAccount, raw_token: str) -> PushDevice:
    token = push_rules.validate_token(raw_token)
    now = ctx.clock.now()
    device = ctx.db.scalar(select(PushDevice).where(PushDevice.token == token))
    if device is None:
        count = ctx.db.scalar(select(func.count()).select_from(PushDevice).where(PushDevice.user_id == actor.id))
        if (count or 0) >= push_rules.MAX_DEVICES_PER_USER:
            raise ConflictError("TOO_MANY_DEVICES", "Ya tienes 5 teléfonos con avisos. Quita uno para sumar otro.")
        device = PushDevice(user_id=actor.id, token=token, created_at=now, last_seen_at=now)
        ctx.db.add(device)
    device.user_id, device.last_seen_at = actor.id, now  # el teléfono pudo cambiar de cuenta
    ctx.db.flush()
    sent = _sent(ctx, actor.id)
    _mark(ctx, actor.id, [key for key, _kind in _keys(ctx, actor) if key not in sent])
    return device


def unregister(ctx: ServiceContext, actor: UserAccount, raw_token: str) -> None:
    ctx.db.execute(delete(PushDevice).where(PushDevice.user_id == actor.id,
                                            PushDevice.token == raw_token.strip()))


def collect(ctx: ServiceContext) -> list[Outgoing]:
    """Una ronda: para cada persona con teléfono, los pendientes nuevos se marcan y se juntan en un aviso."""
    tokens: dict[int, list[str]] = {}
    for device in ctx.db.scalars(select(PushDevice).order_by(PushDevice.id)):
        tokens.setdefault(device.user_id, []).append(device.token)
    out = []
    for user in ctx.db.scalars(select(UserAccount).where(UserAccount.id.in_(list(tokens)))):
        sent = _sent(ctx, user.id)
        fresh = [(key, kind) for key, kind in _keys(ctx, user) if key not in sent]
        if fresh:
            _mark(ctx, user.id, [key for key, _kind in fresh])
            out.append(Outgoing(user.id, tokens[user.id], push_rules.body_for([kind for _key, kind in fresh])))
    return out


def forget_tokens(ctx: ServiceContext, dead: list[str]) -> None:
    """Expo avisa que esos teléfonos ya no aceptan avisos (app borrada o permiso quitado)."""
    if dead:
        ctx.db.execute(delete(PushDevice).where(PushDevice.token.in_(dead)))
