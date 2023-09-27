# -*- coding: utf-8 -*-
from flask import Flask

from flask_foundation.factory import create_app


def test_app_factory():
    app = create_app()
    assert isinstance(app, Flask)
