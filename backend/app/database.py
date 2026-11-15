import os
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from ml.data import ROOT

(ROOT / "runtime").mkdir(exist_ok=True)
URL = os.getenv("JALSATHI_DATABASE", f"sqlite:///{(ROOT / 'runtime/jalsathi.db').as_posix()}")
engine = create_engine(URL, connect_args={"check_same_thread": False} if URL.startswith("sqlite") else {})
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


Base.metadata.create_all(engine)
