from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    git_url: Mapped[str] = mapped_column(String)
    domain: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    status: Mapped[str] = mapped_column(String, default="Pending")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="projects")