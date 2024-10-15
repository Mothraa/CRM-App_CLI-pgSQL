import os
from datetime import datetime
import pytz
from enum import Enum

import yaml
from dotenv import load_dotenv
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLAEnum, MetaData
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import as_declarative



# TODO : ne pas lire plusieurs fois les fichiers de param, a centraliser au démarrage de l'app
# chargement du nom du schema depuis l'environnement (.env)
load_dotenv()
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")
metadata_obj = MetaData(schema=DATABASE_SCHEMA)

# TODO : ne pas lire plusieurs fois les fichiers de param, a centraliser au démarrage de l'app
# récupération de la time_zone depuis le fichier config.yaml
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)
TIME_ZONE_NAME = config['global']['TIME_ZONE']
TIME_ZONE = pytz.timezone(TIME_ZONE_NAME)


# décorateur sqlalchemy pour rendre la class déclarative => champs et methods en commun aux class enfant.
@as_declarative()
class Base(DeclarativeBase):
    # pour stocker les tables dans le schema DATABASE_SCHEMA
    metadata = metadata_obj

    # champs en commun entre toutes les tables
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 default=lambda: datetime.now(TIME_ZONE))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)


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

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    # TODO : déplacer les roles dans une table spécifique.
    role: Mapped[RoleType] = mapped_column(SQLAEnum(RoleType), nullable=False)

    customers: Mapped[list["Customer"]] = relationship(back_populates="sales_contact")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="sales_contact")
    events_support: Mapped[list["Event"]] = relationship(back_populates="support_contact")


class Customer(Base):
    """ Model for the customers """
    __tablename__ = "customer"

    company_name: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    # TODO : eviter d'indiquer le schema (tout du moins en dur) pour la foreignkey
    contact_sales_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    sales_contact: Mapped["User"] = relationship(back_populates="customers")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="customer")


class Contract(Base):
    """ Model for the contracts """
    __tablename__ = "contract"

    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    contact_sales_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=True)
    remaining_amount: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[ContractStatus] = mapped_column(SQLAEnum(ContractStatus), nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="contracts")
    sales_contact: Mapped["User"] = relationship(back_populates="contracts")
    events: Mapped[list["Event"]] = relationship(back_populates="contract")


class Event(Base):
    """ Model for the events """
    __tablename__ = "event"

    name: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    start_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    attendees: Mapped[str] = mapped_column(String, nullable=True)
    comments: Mapped[str] = mapped_column(String, nullable=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"), nullable=False)
    contact_support_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    contract: Mapped["Contract"] = relationship(back_populates="events")
    support_contact: Mapped["User"] = relationship(back_populates="events_support")
