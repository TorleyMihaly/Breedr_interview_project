from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(String(255), unique=True)

    cows: Mapped[list["Cow"]] = relationship(
        back_populates="farmer",
        cascade="all, delete-orphan"
    )

class Cow(Base):
    __tablename__ = "cows"
    