# -*- coding: utf-8 -*-
import datetime
import re

from pythonjsonlogger import jsonlogger

from flask_foundation import config, utils


def add_app_name(logger, log_method, event_dict: dict) -> dict:
    event_dict["application"] = config.APPLICATION_NAME
    return event_dict


def combined_logformat(logger, name, event_dict: dict) -> dict:
    if event_dict.get("logger") == "gunicorn.access":
        message = event_dict["message"]
        parts = [
            r"(?P<host>\S+)",  # host %h
            r"\S+",  # indent %l (unused)
            r"(?P<user>\S+)",  # user %u
            r"\[(?P<time>.+)\]",  # time %t
            r'"(?P<request>.+)"',  # request "%r"
            r"(?P<status>[0-9]+)",  # status %>s
            r"(?P<size>\S+)",  # size %b (careful, can be '-')
            r'"(?P<referer>.*)"',  # referer "%{Referer}i"
            r'"(?P<agent>.*)"',  # user agent "%{User-agent}i"
        ]
        pattern = re.compile(r"\s+".join(parts) + r"\s*\Z")
        m = pattern.match(message)
        res = m.groupdict()

        if res["user"] == "-":
            res["user"] = None

        res["status"] = int(res["status"])

        if res["size"] == "-":
            res["size"] = 0
        else:
            res["size"] = int(res["size"])

        if res["referer"] == "-":
            res["referer"] = None

        event_dict.update(res)

    return event_dict


class JsonLogFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: dict, record, message_dict: dict) -> None:
        for field in self._required_fields:
            log_record[field] = record.__dict__.get(field)
        log_record.update(message_dict)

        if "timestamp" not in log_record:
            now = utils.current_timestamp()
            log_record["timestamp"] = datetime.datetime.strftime(
                now, format=config.settings.default.LOG_TIMESTAMP_FORMAT
            )

        if "application" not in log_record:
            log_record["application"] = config.APPLICATION_NAME

        jsonlogger.merge_record_extra(
            record, log_record, reserved=self._skip_fields
        )
