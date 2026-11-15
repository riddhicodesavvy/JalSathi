"""Apply initial durable schema; reruns are idempotent and do not import local history."""

from sqlalchemy import Column, MetaData, String, Table, insert, select

from backend.app.database import Base, engine


def main():
    Base.metadata.create_all(engine)
    versions = Table("jalsathi_schema_versions", MetaData(), Column("version", String, primary_key=True))
    versions.create(engine, checkfirst=True)
    with engine.begin() as connection:
        if connection.scalar(select(versions.c.version).where(versions.c.version == "001_initial")) is None:
            connection.execute(insert(versions).values(version="001_initial"))
    print("JalSathi schema 001_initial is ready; existing records preserved.")


if __name__ == "__main__":
    main()
