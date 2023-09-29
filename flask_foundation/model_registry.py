# -*- coding: utf-8 -*-
def load_models():
    from flask_foundation.auth.models import (  # noqa
        Permission,
        Role,
        User,
        permissions_roles,
        permissions_users,
        roles_users,
    )
