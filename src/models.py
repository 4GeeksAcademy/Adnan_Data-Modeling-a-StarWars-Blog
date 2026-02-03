import os
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(80), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def serialize(self):
        return {"id": self.id, "email": self.email, "is_active": self.is_active}


class People(db.Model):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="people",
        cascade="all, delete-orphan"
    )

    def serialize(self):
        return {"id": self.id, "uid": self.uid, "name": self.name}


class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="planet",
        cascade="all, delete-orphan"
    )

    def serialize(self):
        return {"id": self.id, "uid": self.uid, "name": self.name}


class Favorite(db.Model):
    """
    A Favorite belongs to one User and references either:
    - one People row OR
    - one Planet row
    """
    __tablename__ = "favorite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    # one of these is set per favorite
    people_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("people.id"), nullable=True)
    planet_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("planet.id"), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    people: Mapped["People"] = relationship("People", back_populates="favorites")
    planet: Mapped["Planet"] = relationship("Planet", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("user_id", "people_id", name="uq_user_people_fav"),
        UniqueConstraint("user_id", "planet_id", name="uq_user_planet_fav"),
    )

    def serialize(self):
        if self.people is not None:
            return {"id": self.id, "user_id": self.user_id, "type": "people", "uid": self.people.uid, "name": self.people.name}
        if self.planet is not None:
            return {"id": self.id, "user_id": self.user_id, "type": "planet", "uid": self.planet.uid, "name": self.planet.name}
        return {"id": self.id, "user_id": self.user_id, "type": "unknown"}


# ---------------------------------------------------------
# Diagram generation (creates diagram.png in repo root)
# ---------------------------------------------------------
if __name__ == "__main__":
    from eralchemy2 import render_er

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(ROOT_DIR, "diagram.png")

    render_er(db.Model, out_path)
    print(f"✅ diagram generated at: {out_path}")
