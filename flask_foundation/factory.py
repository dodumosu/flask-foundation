# -*- coding: utf-8 -*-
import logging
import logging.config

import structlog
from bitmapist import SYSTEMS
from dynaconf import FlaskDynaconf
from flask import Flask, Response, request
from flask_request_id import RequestID
from redis import StrictRedis

from flask_foundation import config, loggers, utils


def create_app(custom_settings: dict = None) -> Flask:
    setup_logging()
    setup_bitmapist()

    app = Flask(__name__, instance_relative_config=True)
    RequestID(app=app, generator_func=utils.generate_uuid_string)

    # configure the application instance
    FlaskDynaconf(
        app=app,
        instance_relative_config=True,
        dynaconf_instance=config.settings,
    )

    # override settings
    if custom_settings:
        app.config.from_mapping(custom_settings)

    logger = structlog.get_logger()

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_error_logger.handlers[:]

    @app.after_request
    def log_after_request(response: Response) -> Response:
        request_id = request.environ.get("FLASK_REQUEST_ID")
        logger.info(
            message="request complete",
            request_id=request_id,
            url=request.url,
            response={
                "status": response.status,
                "status_code": response.status_code,
            },
        )

        return response

    return app


def setup_bitmapist(system_name: str = None) -> None:
    system_name = system_name or config.settings.default.BITMAPIST_SYSTEM_NAME
    bitmapist_redis_url = config.settings.default.BITMAPIST_REDIS_URL
    system_redis_url = config.settings.default.REDIS_URL
    SYSTEMS[system_name] = StrictRedis.from_url(
        bitmapist_redis_url or system_redis_url
    )


def setup_logging() -> None:
    timestamper = structlog.processors.TimeStamper(
        fmt=config.settings.default.LOG_TIMESTAMP_FORMAT
    )
    pre_chain = [
        loggers.add_app_name,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(colors=False),
                    "foreign_pre_chain": pre_chain,
                },
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                    "foreign_pre_chain": pre_chain,
                },
            },
            "handlers": {
                "development": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "console",
                },
                "production": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                },
            },
            "loggers": {"": {"level": "DEBUG", "propagate": True}},
        }
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            loggers.add_app_name,
            loggers.combined_logformat,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(
                fmt=config.settings.default.LOG_TIMESTAMP_FORMAT
            ),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
