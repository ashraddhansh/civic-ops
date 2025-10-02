"""increase_url_column_sizes

Revision ID: ab92b9c1eebd
Revises: be97e5d0d30e
Create Date: 2025-10-02 15:41:13.098638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab92b9c1eebd'
down_revision: Union[str, Sequence[str], None] = 'be97e5d0d30e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Increase photo_url and voice_note_url column sizes to accommodate pre-signed URLs
    op.alter_column('issues', 'photo_url',
                    existing_type=sa.String(255),
                    type_=sa.String(1000),
                    existing_nullable=True)
    
    op.alter_column('issues', 'voice_note_url',
                    existing_type=sa.String(255),
                    type_=sa.String(1000),
                    existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert photo_url and voice_note_url column sizes back to 255
    op.alter_column('issues', 'photo_url',
                    existing_type=sa.String(1000),
                    type_=sa.String(255),
                    existing_nullable=True)
    
    op.alter_column('issues', 'voice_note_url',
                    existing_type=sa.String(1000),
                    type_=sa.String(255),
                    existing_nullable=True)
