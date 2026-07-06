from datetime import date, datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
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
    __table_args__ = (
        UniqueConstraint("farmer_id", "tag_number", name="cow_farmer_combination")
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tag_number: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    breed: Mapped[str | None] = mapped_column(String(120), nullable=True)
    date_of_birth: Mapped[date] = mapped_column(nullable=False)

    farmer_id: Mapped[int] = mapped_column(
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False
    )

    farmer: Mapped["Farmer"] = relationship(back_populates="cows")
    measurement: Mapped[list["CowMeasurement"]] = relationship(
        back_populates="cow",
        cascade="all, delete-orphan",
        order_by=lambda: CowMeasurement.recorder_at.desc()
    )

    @property
    def age(self) -> int:
        return (date.today() - self.date_of_birth).days
    
class CowMeasurement(Base):
    __tablename__ = "cow_measurements"
    __table_args__ = (
                CheckConstraint("weight_kg IS NULL OR weight_kg > 0", name="weight_check"),
                CheckConstraint("height_cm IS NULL OR height_cm > 0", name="height_check"),
                CheckConstraint("hearth_girth_cm IS NULL OR hearth_girth_cm > 0", name="hearth_girth_check"),
                CheckConstraint("body_condition_score IS NULL OR body_condition_score BETWEEN 1 and 5", name="body_condition_score_check")
            )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    cow_id: Mapped[int] = mapped_column(
        ForeignKey("cows.id", ondelete="CASCADE"),
        nullable=False
    )

    recorder_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    height_cm: Mapped[float | None] = mapped_column(nullable=True)
    heart_girth_cm: Mapped[float | None] = mapped_column(nullable=True)
    body_condition_score: Mapped[float | None] = mapped_column(nullable=True)

    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    cow: Mapped["Cow"] = relationship(back_populates="measurements")
