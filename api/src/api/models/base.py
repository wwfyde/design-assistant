from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions
convention = {
    "ix": "ix_%(column_0_label)s",  # index
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # unique constraint
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # check constraint
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # foreign key
    "pk": "pk_%(table_name)s",  # primary key
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata
    pass
