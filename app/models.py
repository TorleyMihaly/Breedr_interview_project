from datetime import date, datetime, timezone

from helpers.global_restrictions import email_length, tag_number_length, cow_name_length, cow_breed_length, measurements_notes_length

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class FarmerModel(Base):
    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(String(email_length), unique=True)

    cows: Mapped[list["CowModel"]] = relationship(
        back_populates="farmer",
        cascade="all, delete-orphan"
    )

class CowModel(Base):
    __tablename__ = "cows"
    __table_args__ = (
        UniqueConstraint("farmer_id", "tag_number", name="cow_farmer_combination"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tag_number: Mapped[str] = mapped_column(String(tag_number_length), nullable=False)
    name: Mapped[str | None] = mapped_column(String(cow_name_length), nullable=True)
    breed: Mapped[str | None] = mapped_column(String(cow_breed_length), nullable=True)
    date_of_birth: Mapped[date] = mapped_column(nullable=False)

    farmer_id: Mapped[int] = mapped_column(
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False
    )

    farmer: Mapped["FarmerModel"] = relationship(back_populates="cows")
    measurements: Mapped[list["CowMeasurementModel"]] = relationship(
        back_populates="cow",
        cascade="all, delete-orphan",
        order_by=lambda: CowMeasurementModel.recorded_at.desc()
    )

    @property
    def age_days(self) -> int:
        return (date.today() - self.date_of_birth).days
    
class CowMeasurementModel(Base):
    __tablename__ = "cow_measurements"
    __table_args__ = (
                CheckConstraint("weight_kg IS NULL OR weight_kg > 0", name="weight_check"),
                CheckConstraint("height_cm IS NULL OR height_cm > 0", name="height_check"),
                CheckConstraint("heart_girth_cm IS NULL OR heart_girth_cm > 0", name="heart_girth_check"),
                CheckConstraint("body_condition_score IS NULL OR body_condition_score BETWEEN 1 and 5", name="body_condition_score_check"),
            )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    cow_id: Mapped[int] = mapped_column(
        ForeignKey("cows.id", ondelete="CASCADE"),
        nullable=False
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    height_cm: Mapped[float | None] = mapped_column(nullable=True)
    heart_girth_cm: Mapped[float | None] = mapped_column(nullable=True)
    body_condition_score: Mapped[float | None] = mapped_column(nullable=True)

    notes: Mapped[str | None] = mapped_column(String(measurements_notes_length), nullable=True)

    cow: Mapped["CowModel"] = relationship(back_populates="measurements")
