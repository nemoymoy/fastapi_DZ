import datetime
import uuid
from sqlalchemy import DateTime, Integer, String, Text, func, ForeignKey, UUID, Numeric
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from custom_types import ROLE

from config import POSTGRES_DSN

engine = create_async_engine(POSTGRES_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    @property
    def id_dict(self):
        return {"id": self.id}

class Token(Base):
    __tablename__ = "token"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, server_default=func.gen_random_uuid())
    creation_token: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(column="user.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship(argument="User", lazy="joined", back_populates="tokens")

    @property
    def dict(self):
        return {"token": self.token}


class Advert(Base):
    __tablename__ = "advert"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=False, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, unique=False, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), unique=False, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey(column="user.id", ondelete="CASCADE"), nullable=False)
    author: Mapped["User"] = relationship(argument="User", lazy="joined", back_populates="adverts")
    # author = relationship(argument="User", back_populates="adverts", lazy="joined")

    @property
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "created_at": self.created_at.isoformat(),
            "author_id": self.author_id,
        }


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    registration_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    tokens: Mapped[list[Token]] = relationship(Token, lazy="joined", back_populates="user", cascade="all, delete-orphan")
    adverts: Mapped[list[Advert]] = relationship(Advert, lazy="joined", back_populates="author", cascade="all, delete-orphan", passive_deletes=True)
    role: Mapped[ROLE] = mapped_column(String, default="user")
    # adverts = relationship(argument="Advert", back_populates="author", cascade="all, delete", passive_deletes=True, lazy="joined")

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "registration_time": self.registration_time.isoformat(),
            "tokens": self.tokens,
            "adverts": self.adverts,
            "role": self.role,
        }


ORM_OBJ = Advert | User | Token
ORM_CLS = type[Advert] | type[User] | type[Token]

async def init_orm():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def close_orm():
    await engine.dispose()
