# -*- coding: utf-8 -*-
from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False,  # prefix disabled if set to False
    merge_enabled=True,
    settings_files=["settings.toml", ".secrets.toml"],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.

project_root = Path(__file__).parent.parent

APPLICATION_NAME = "Flask App"
