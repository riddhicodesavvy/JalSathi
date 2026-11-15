import os
from pathlib import Path

import pytest

TEST_DB = Path(__file__).resolve().parents[2] / "runtime/test.sqlite"
os.environ["JALSATHI_DATABASE"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["JALSATHI_REPORTS"] = str(TEST_DB.parent / "test-reports")


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.database import Analysis, Batch, Session

    with Session.begin() as session:
        session.query(Analysis).delete()
        session.query(Batch).delete()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample():
    from ml.data import FEATURES, load_dataset

    frame, _ = load_dataset()
    return frame.dropna().iloc[0][FEATURES].to_dict()
