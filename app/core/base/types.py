from typing import Any

from pydantic import TypeAdapter
from sqlalchemy import Dialect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator


class PydanticType(TypeDecorator):
    """Custom column type that encodes/decodes the value using Pydantic TypeAdapter

    SAVING:
    - Uses SQLAlchemy JSON type under the hood.
    - Accepts any type supported by Pydantic's TypeAdapter and converts it to a dict on save.
    - SQLAlchemy engine JSON-encodes the dict to a string.

    RETRIEVING:
    - Pulls the string from the database.
    - SQLAlchemy engine JSON-decodes the string to a dict.
    - Validates the dict using the Type Adapter.
    """

    impl = JSONB
    cache_ok = True

    def __init__(self, pydantic_type: type) -> None:
        super().__init__()
        self.type_adapter = TypeAdapter(pydantic_type)

    def process_bind_param(self, value: Any, dialect: Dialect) -> Any:
        if value is None:
            return None

        return self.type_adapter.dump_python(value, mode="json")

    def process_result_value(self, value: Any, dialect: Dialect) -> Any:
        if value is None:
            return None

        return self.type_adapter.validate_python(value)
