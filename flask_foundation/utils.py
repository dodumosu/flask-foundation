# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from uuid import UUID

import uuid_utils


def current_timestamp() -> datetime:
    return datetime.now(tz=timezone.utc)


def generate_uuid() -> UUID:
    return UUID(bytes=uuid_utils.uuid7().bytes)


def generate_uuid_string() -> str:
    return generate_uuid().hex
