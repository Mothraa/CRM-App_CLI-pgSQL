from datetime import datetime
from enum import Enum

from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLAEnum, MetaData
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column

from .config_loader import TIME_ZONE, DATABASE_SCHEMA

metadata_obj = MetaData(schema=DATABASE_SCHEMA)


# # décorateur sqlalchemy pour rendre la class déclarative => champs et methods en commun aux class enfant.
# @as_declarative()
class Base(DeclarativeBase):
    # pour stocker les tables dans le schema DATABASE_SCHEMA
    metadata = metadata_obj


# evolution : déplacer les roles dans une table spécifique.
class RoleType(str, Enum):
    admin = "admin"
    manage = "manage"
    sales = "sales"
    support = "support"


class ContractStatus(str, Enum):
    to_send = "to_send"
    pending = "pending"
    canceled = "canceled"
    signed = "signed"
    finished = "finished"


class User(Base):
    """ Model for the app users"""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[RoleType] = mapped_column(SQLAEnum(RoleType), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 default=lambda: datetime.now(TIME_ZONE))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    customers: Mapped[list["Customer"]] = relationship(back_populates="sales_contact")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="sales_contact")
    events_support: Mapped[list["Event"]] = relationship(back_populates="support_contact")


class Customer(Base):
    """ Model for the customers """
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    contact_sales_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 default=lambda: datetime.now(TIME_ZONE))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    sales_contact: Mapped["User"] = relationship(back_populates="customers")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="customer")


class Contract(Base):
    """ Model for the contracts """
    __tablename__ = "contract"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    contact_sales_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=True)
    remaining_amount: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[ContractStatus] = mapped_column(SQLAEnum(ContractStatus), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 default=lambda: datetime.now(TIME_ZONE))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="contracts")
    sales_contact: Mapped["User"] = relationship(back_populates="contracts")
    events: Mapped[list["Event"]] = relationship(back_populates="contract")


class Event(Base):
    """ Model for the events """
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    start_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    attendees: Mapped[str] = mapped_column(String, nullable=True)
    comments: Mapped[str] = mapped_column(String, nullable=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"), nullable=False)
    contact_support_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 default=lambda: datetime.now(TIME_ZONE))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    contract: Mapped["Contract"] = relationship(back_populates="events")
    support_contact: Mapped["User"] = relationship(back_populates="events_support")
