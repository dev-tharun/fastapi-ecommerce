"""add the product table column

Revision ID: 91072e28fdb4
Revises: 9be5dc52e521
Create Date: 2025-02-28 12:50:16.976501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91072e28fdb4'
down_revision: Union[str, None] = '9be5dc52e521'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('discount_product_price', sa.DECIMAL(precision=10, scale=2), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'discount_product_price')
    # ### end Alembic commands ###
