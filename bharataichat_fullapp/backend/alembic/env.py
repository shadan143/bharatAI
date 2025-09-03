from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.db import Base
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata
def run_migrations_offline():
    pass
def run_migrations_online():
    pass
