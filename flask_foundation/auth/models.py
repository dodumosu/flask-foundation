# -*- coding: utf-8 -*-
import enum
from datetime import datetime
from typing import List
from uuid import UUID

import sqlalchemy as sa
from flask_security import RoleMixin, UserMixin
from flask_security.utils import hash_password
from sqlalchemy.dialects.postgresql import UUID as UUIDField
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils.types import ChoiceType

from flask_foundation.db import modelbase
from flask_foundation.utils import generate_uuid

permissions_roles = sa.Table(
    "permissions_roles",
    modelbase.Base.metadata,
    sa.Column(
        "permission_id",
        UUIDField,
        sa.ForeignKey("permissions.id", ondelete="CASCADE"),
    ),
    sa.Column(
        "role_id", UUIDField, sa.ForeignKey("roles.id", ondelete="CASCADE")
    ),
)

permissions_users = sa.Table(
    "permissions_users",
    modelbase.Base.metadata,
    sa.Column(
        "permission_id",
        UUIDField,
        sa.ForeignKey("permissions.id", ondelete="CASCADE"),
    ),
    sa.Column(
        "user_id", UUIDField, sa.ForeignKey("users.id", ondelete="CASCADE")
    ),
)

roles_users = sa.Table(
    "roles_users",
    modelbase.Base.metadata,
    sa.Column(
        "role_id",
        UUIDField,
        sa.ForeignKey("roles.id", ondelete="CASCADE"),
    ),
    sa.Column(
        "user_id", UUIDField, sa.ForeignKey("users.id", ondelete="CASCADE")
    ),
)


class Gender(str, enum.Enum):
    FEMALE = "female"
    MALE = "male"
    UNSPECIFIED = "unspecified"

    @classmethod
    def lookup(cls, specifier: str):
        spec = specifier.lower()[0]
        gender_map = {v._value_[0]: v for v in cls.__members__}

        return gender_map.get(spec, cls.UNSPECIFIED)


class Permission(modelbase.BaseModel):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(sa.String)


class Role(modelbase.BaseModel, RoleMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(sa.String)

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary=permissions_roles
    )
    users: Mapped[List["User"]] = relationship(
        "User", back_populates="roles", secondary=roles_users
    )


class User(modelbase.BaseModel, UserMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(sa.String)
    first_name: Mapped[str] = mapped_column(sa.String)
    last_name: Mapped[str] = mapped_column(sa.String)
    gender: Mapped[Gender] = mapped_column(
        ChoiceType(Gender, impl=sa.String()),
        default=Gender.UNSPECIFIED,
        nullable=False,
    )
    location: Mapped[str] = mapped_column(sa.String)
    last_login_at: Mapped[datetime] = mapped_column(sa.DateTime)
    current_login_at: Mapped[datetime] = mapped_column(sa.DateTime)
    last_login_ip: Mapped[str] = mapped_column(sa.String)
    current_login_ip: Mapped[str] = mapped_column(sa.String)
    login_count: Mapped[int] = mapped_column(sa.Integer)
    active: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False
    )
    fs_uniquifier: Mapped[UUID] = mapped_column(
        UUIDField, default=generate_uuid, nullable=False, unique=True
    )

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary=permissions_users
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role", back_populates="users", secondary=roles_users
    )

    def set_password(self, new_password: str) -> None:
        self.password = hash_password(new_password)
