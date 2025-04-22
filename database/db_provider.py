from database.db import Db
_db: Db | None = None

def set_db_instance(db: Db):
    global _db
    _db = db

def get_db() -> Db:
    if _db is None:
        raise RuntimeError("Database not initialized!")
    return _db