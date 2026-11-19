"""Jednorázová migrace původního sports_data.json do PostgreSQL."""
import os
from dotenv import load_dotenv
load_dotenv()
from core.db import Base, engine
from core import models  # noqa
from core.migration import import_legacy_json

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    result = import_legacy_json("sports_data.json")
    print(result)
