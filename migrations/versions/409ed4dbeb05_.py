"""empty message

Revision ID: 409ed4dbeb05
Revises: 
Create Date: 2019-12-29 09:48:12.218656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "409ed4dbeb05"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=256), nullable=False),
        sa.Column("pw_hash", sa.Binary(), nullable=False),
        sa.Column("auth_fail", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "role_user_map",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"],),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"],),
    )
    op.execute("INSERT INTO role (name) VALUES ('user');")
    op.execute("INSERT INTO role (name) VALUES ('admin');")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("role_user_map")
    op.drop_table("user")
    op.drop_table("role")
    # ### end Alembic commands ###
