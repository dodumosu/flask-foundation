# -*- coding: utf-8 -*-
import multiprocessing

from flask_foundation.config import settings

workers = int(
    settings.default.get("NUM_WORKERS", multiprocessing.cpu_count() / 2 + 1)
)
timeout = 120
preload_app = True
