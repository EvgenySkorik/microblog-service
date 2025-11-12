import os
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from microblog.config import settings
from microblog.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    api_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    tweets: Mapped[list["Tweet"]] = relationship(
        back_populates="author",
        cascade="all, delete, delete-orphan",
    )

    liked_tweets: Mapped[list["Tweet"]] = relationship(
        secondary="tweet_likes", back_populates="likes"
    )

    # Подписчики связь
    followers: Mapped[list["User"]] = relationship(
        secondary="user_followers",
        primaryjoin="User.id == user_followers.c.following_id",
        secondaryjoin="User.id == user_followers.c.follower_id",
        back_populates="following",
    )

    # На кого подписан связь
    following: Mapped[list["User"]] = relationship(
        secondary="user_followers",
        primaryjoin="User.id == user_followers.c.follower_id",
        secondaryjoin="User.id == user_followers.c.following_id",
        back_populates="followers",
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    author: Mapped["User"] = relationship(back_populates="tweets")

    likes: Mapped[list["User"]] = relationship(
        secondary="tweet_likes", back_populates="liked_tweets"
    )

    attachments: Mapped[list["Media"]] = relationship(
        back_populates="tweet", cascade="all, delete-orphan"
    )


class Media(Base):
    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(300))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    tweet_id: Mapped[int | None] = mapped_column(
        ForeignKey("tweets.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship()
    tweet: Mapped[Optional["Tweet"]] = relationship(
        back_populates="attachments",
    )

    @property
    def url(self) -> str:
        return f"{settings.MEDIA.MEDIA_URL}{os.path.basename(self.path)}"


user_followers_association = Table(
    "user_followers",
    Base.metadata,
    Column(
        "follower_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "following_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=datetime.now(UTC),
    ),
)

tweet_like_association = Table(
    "tweet_likes",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tweet_id",
        Integer,
        ForeignKey("tweets.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=datetime.now(UTC),
    ),
)
