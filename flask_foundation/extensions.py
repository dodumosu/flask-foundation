# -*- coding: utf-8 -*-
from flask_caching import Cache
from flask_cors import CORS
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
mail = Mail()
security = Security()
session = Session()
talisman = Talisman()
