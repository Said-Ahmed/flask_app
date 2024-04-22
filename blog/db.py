from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = 'sqlite:///my_db.db'
engine = create_engine(url=DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)

session = Session()

Base = declarative_base()


def init_db():
    import blog.models
    Base.metadata.create_all(bind=engine)