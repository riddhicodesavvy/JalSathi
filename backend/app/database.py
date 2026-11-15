import os
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import NullPool

from ml.data import ROOT

PRODUCTION = os.getenv("VERCEL") == "1" or os.getenv("JALSATHI_ENV") == "production"


def database_url():
    value = os.getenv("JALSATHI_DATABASE") or os.getenv("DATABASE_URL")
    if not value:
        if PRODUCTION:
            raise RuntimeError(
                "Production requires a durable DATABASE_URL; local SQLite is not persistent on Vercel."
            )
        (ROOT / "runtime").mkdir(exist_ok=True)
        value = f"sqlite:///{(ROOT / 'runtime/jalsathi.db').as_posix()}"
    if value.startswith("postgres://"):
        value = value.replace("postgres://", "postgresql+psycopg://", 1)
    elif value.startswith("postgresql://"):
        value = value.replace("postgresql://", "postgresql+psycopg://", 1)
    if PRODUCTION and value.startswith("sqlite"):
        raise RuntimeError("Production SQLite would be ephemeral; configure a durable PostgreSQL database.")
    return value


URL = database_url()
options = (
    dict(connect_args={"check_same_thread": False})
    if URL.startswith("sqlite")
    else dict(poolclass=NullPool, pool_pre_ping=True)
)
engine = create_engine(URL, **options)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    source: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON)
    report_path: Mapped[str | None] = mapped_column(String, nullable=True)


class Batch(Base):
    __tablename__ = "batches"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    payload: Mapped[dict] = mapped_column(JSON)


if not PRODUCTION:
    Base.metadata.create_all(engine)
