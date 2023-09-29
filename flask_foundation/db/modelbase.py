# -*- coding: utf-8 -*-
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from shortuuid import encode
from sqlalchemy.dialects.postgresql import UUID as UUIDField
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from flask_foundation.db.sessions import db_session
from flask_foundation.utils import generate_uuid


class Base(DeclarativeBase):
    __abstract__ = True

    # this is needed for flask-security to work
    query = db_session.query_property()


class CommonMixin:
    id: Mapped[UUID] = mapped_column(
        UUIDField, default=generate_uuid, primary_key=True
    )

    @property
    def uid(self) -> str:
        return encode(self.id) if self.id else None


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("timezone('utc', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.text("timezone('utc', now())"),
        server_onupdate=sa.text("timezone('utc', now())"),
    )


class BaseModel(Base, CommonMixin, TimestampMixin):
    __abstract__ = True
