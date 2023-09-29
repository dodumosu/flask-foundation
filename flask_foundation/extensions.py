# -*- coding: utf-8 -*-
from flask_caching import Cache
from flask_cors import CORS
try:
    from flask_debugtoolbar import DebugToolbarExtension
    fdt_available = True
except ImportError:
    fdt_available = False
from flask_mailman import Mail
from flask_security import Security
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

from flask_foundation.db.modelbase import Base

cache = Cache()
cors = CORS()
csrf = CSRFProtect()
db = SQLAlchemy(model_class=Base, metadata=Base.metadata)
debug_toolbar = DebugToolbarExtension() if fdt_available else None
mail = Mail()
security = Security()
session = Session()
talisman = Talisman()
