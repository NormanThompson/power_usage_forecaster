from functools import lru_cache

from sqlalchemy import Engine, Table, create_engine
from sqlalchemy.dialects.postgresql import insert

from forecast.config import get_settings
from forecast.db.models import metadata


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url)


def create_tables() -> None:
    metadata.create_all(get_engine())


def upsert(table: Table, rows: list[dict], batch_size: int = 5000) -> int:
    """Insert rows, overwriting non-key columns on primary-key conflict (idempotent)."""
    if not rows:
        return 0
    pk = [c.name for c in table.primary_key.columns]
    with get_engine().begin() as conn:
        for i in range(0, len(rows), batch_size):
            stmt = insert(table).values(rows[i : i + batch_size])
            update_cols = {
                c.name: stmt.excluded[c.name] for c in table.columns if c.name not in pk
            }
            conn.execute(stmt.on_conflict_do_update(index_elements=pk, set_=update_cols))
    return len(rows)
