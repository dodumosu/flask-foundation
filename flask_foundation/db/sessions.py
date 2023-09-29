# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_foundation.config import settings

engine = create_engine(
    settings.default.SQLALCHEMY_DATABASE_URI,
    connect_args={"options": "-c timezone=utc"},
    echo=bool(settings.default.get("SQLALCHEMY_ECHO_ON", False)),
)
db_session = scoped_session(
    sessionmaker(autoflush=False, bind=engine, expire_on_commit=False)
)
