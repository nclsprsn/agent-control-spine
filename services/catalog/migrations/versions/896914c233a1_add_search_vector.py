"""add_search_vector

Revision ID: 896914c233a1
Revises: d01b03d7e7ee
Create Date: 2026-05-16 15:18:39.148990

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "896914c233a1"
down_revision: Union[str, None] = "d01b03d7e7ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TRIGGER_FN = """
CREATE OR REPLACE FUNCTION catalog_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', array_to_string(coalesce(NEW.tags, '{}'::text[]), ' ')), 'C');
    RETURN NEW;
END
$$ LANGUAGE plpgsql;
"""


BACKFILL_EXPR = (
    "setweight(to_tsvector('english', coalesce(name, '')), 'A') || "
    "setweight(to_tsvector('english', coalesce(description, '')), 'B') || "
    "setweight(to_tsvector('english', array_to_string(coalesce(tags, '{}'::text[]), ' ')), 'C')"
)


def upgrade() -> None:
    op.execute(TRIGGER_FN)

    op.execute("ALTER TABLE capabilities ADD COLUMN search_vector tsvector")
    op.execute(
        "CREATE TRIGGER capabilities_search_vector_trg "
        "BEFORE INSERT OR UPDATE OF name, description, tags ON capabilities "
        "FOR EACH ROW EXECUTE FUNCTION catalog_search_vector_update()"
    )
    op.execute(f"UPDATE capabilities SET search_vector = {BACKFILL_EXPR}")
    op.execute("CREATE INDEX ix_capabilities_search_vector ON capabilities USING gin (search_vector)")

    op.execute("ALTER TABLE tools ADD COLUMN search_vector tsvector")
    op.execute(
        "CREATE TRIGGER tools_search_vector_trg "
        "BEFORE INSERT OR UPDATE OF name, description, tags ON tools "
        "FOR EACH ROW EXECUTE FUNCTION catalog_search_vector_update()"
    )
    op.execute(f"UPDATE tools SET search_vector = {BACKFILL_EXPR}")
    op.execute("CREATE INDEX ix_tools_search_vector ON tools USING gin (search_vector)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_tools_search_vector")
    op.execute("DROP TRIGGER IF EXISTS tools_search_vector_trg ON tools")
    op.execute("ALTER TABLE tools DROP COLUMN IF EXISTS search_vector")

    op.execute("DROP INDEX IF EXISTS ix_capabilities_search_vector")
    op.execute("DROP TRIGGER IF EXISTS capabilities_search_vector_trg ON capabilities")
    op.execute("ALTER TABLE capabilities DROP COLUMN IF EXISTS search_vector")

    op.execute("DROP FUNCTION IF EXISTS catalog_search_vector_update()")
