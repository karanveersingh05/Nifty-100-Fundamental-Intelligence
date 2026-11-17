import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
if not database_url:
    use_sqlite = os.getenv('USE_SQLITE', '').lower() in ('1', 'true', 'yes')

    if use_sqlite:
        # Local mode: use a SQLite file — no Postgres needed
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, 'data', 'b100_local.sqlite3')
        database_url = f"sqlite:///{db_path}"
    else:
        # Docker / remote Postgres mode (original behaviour)
        db_user = os.getenv('DB_USER', 'b100_user')
        db_password = os.getenv('DB_PASSWORD', 'b100_password')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'b100_intelligence')
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        if os.getenv('DB_SSLMODE') == 'require' or os.getenv('PGSSLMODE') == 'require':
            database_url += "?sslmode=require"

engine = create_engine(database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_engine():
    return engine
