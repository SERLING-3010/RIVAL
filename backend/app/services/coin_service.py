"""Libro de monedas RIVAL (virtuales, sin valor real). Solo asientos nuevos; el saldo nunca es negativo.

Cada movimiento bloquea la fila del equipo (FOR UPDATE) para que dos gastos simultáneos no
dejen el saldo en negativo.
"""

from sqlalchemy import func, select

from app.domain.manager_rules import STARTING_BUDGET, check_balance, result_rewards
from app.persistence.models_manager import CoinEntry
from app.persistence.models_teams import Team
from app.services.audit_service import record_event
from app.services.context import ServiceContext


def balance(ctx: ServiceContext, team_id: int) -> int:
    return int(ctx.db.scalar(select(func.coalesce(func.sum(CoinEntry.amount), 0)).where(
        CoinEntry.team_id == team_id)) or 0)


def move(ctx: ServiceContext, team_id: int, amount: int, reason: str, reference: str | None,
         actor_id: int | None, actor_type: str = "HUMAN") -> CoinEntry:
    """Agrega un asiento. Si es una resta, exige saldo suficiente (bloquea el equipo antes de leerlo)."""
    ctx.db.get(Team, team_id, with_for_update=True)
    before = balance(ctx, team_id)
    if amount < 0:
        check_balance(before, -amount)
    entry = CoinEntry(team_id=team_id, amount=amount, reason=reason, reference=reference,
                      created_by=actor_id, created_at=ctx.clock.now())
    ctx.db.add(entry)
    ctx.db.flush()
    record_event(ctx, action="COINS_MOVED", entity="team", entity_id=team_id, initiated_by=actor_id,
                 actor_type=actor_type, before={"balance": before},
                 after={"balance": before + amount, "amount": amount, "reason": reason, "reference": reference})
    return entry


def grant_initial(ctx: ServiceContext, team_id: int, actor_id: int) -> None:
    move(ctx, team_id, STARTING_BUDGET, "STARTING_BUDGET", None, actor_id, actor_type="SYSTEM_RULE")


def reward_result(ctx: ServiceContext, contract_id: int, host_team_id: int, guest_team_id: int,
                  host_score: int, guest_score: int) -> None:
    host, guest = result_rewards(host_score, guest_score)
    reference = f"contract:{contract_id}"
    move(ctx, host_team_id, host, "MATCH_REWARD", reference, None, actor_type="SYSTEM_RULE")
    move(ctx, guest_team_id, guest, "MATCH_REWARD", reference, None, actor_type="SYSTEM_RULE")


def history(ctx: ServiceContext, team_id: int, limit: int = 20) -> list[CoinEntry]:
    return list(ctx.db.scalars(select(CoinEntry).where(CoinEntry.team_id == team_id)
                               .order_by(CoinEntry.id.desc()).limit(limit)))
