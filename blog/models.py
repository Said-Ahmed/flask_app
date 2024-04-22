from datetime import datetime
from typing import Annotated

from flask_login import UserMixin
from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, validates

from blog.db import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(default=datetime.now)]
updated_at = Annotated[datetime, mapped_column(
        default=datetime.now,
        onupdate=datetime.now,
    )]


class User(Base, UserMixin):
    __tablename__ = 'users'
    id: Mapped[intpk]
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[intpk]
    title: Mapped[str] = mapped_column(String(50))
    text: Mapped[str] = mapped_column(nullable=True)
    users: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]











