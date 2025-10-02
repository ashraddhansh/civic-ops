"""fix otp_verifications id autoincrement

Revision ID: 39769358bbda
Revises: b2a3af3cf86b
Create Date: 2025-10-02 13:04:32.614688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39769358bbda'
down_revision: Union[str, Sequence[str], None] = 'b2a3af3cf86b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix otp_verifications id column to have proper autoincrement."""
    # Drop existing data and recreate the sequence properly
    op.execute("DELETE FROM otp_verifications")  # Clear existing data
    
    # Set up the sequence properly
    op.execute("DROP SEQUENCE IF EXISTS otp_verifications_id_seq CASCADE")
    op.execute("CREATE SEQUENCE otp_verifications_id_seq")
    op.execute("ALTER TABLE otp_verifications ALTER COLUMN id SET DEFAULT nextval('otp_verifications_id_seq')")
    op.execute("ALTER SEQUENCE otp_verifications_id_seq OWNED BY otp_verifications.id")
    op.execute("SELECT setval('otp_verifications_id_seq', 1, false)")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the sequence
    op.execute("ALTER TABLE otp_verifications ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS otp_verifications_id_seq CASCADE")
