"""
models.py
=====================================================================
Modelos SQLAlchemy 2.0 (declarative + typing) para o backend
FastAPI da clínica veterinária (cães e gatos) + Infraestrutura MySQL.

Todas as tabelas e colunas foram traduzidas para o inglês.
Convenção de chave primária: id_<entidade> (ex: id_animal, id_owner).

Requer: sqlalchemy >= 2.0, pymysql
=====================================================================
"""

from __future__ import annotations

import enum
import datetime
import os
from datetime import date, time

from sqlalchemy import (
    create_engine,
    ForeignKey,
    UniqueConstraint,
    Index,
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    Time,
    Integer,
    Numeric,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped, 
    mapped_column, 
    relationship,
    sessionmaker,
)


class Base(DeclarativeBase):
    pass


# =====================================================================
# ENUMS (regras de domínio aplicadas via SQLAlchemy Enum / CHECK)
# =====================================================================

class Species(str, enum.Enum):
    DOG = "dog"
    CAT = "cat"


class Sex(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class ExamStatus(str, enum.Enum):
    REQUESTED = "requested"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ExamResult(str, enum.Enum):
    NORMAL = "normal"
    ALTERED = "altered"
    INCONCLUSIVE = "inconclusive"


# =====================================================================
# ROLE (roles.role_id -> id_role, padronizado)
# =====================================================================

class Role(Base):
    __tablename__ = "roles"

    id_role: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self) -> str:
        return f"<Role id={self.id_role} name={self.role_name!r}>"


# =====================================================================
# USER (usuarios -> users). Admin e sub-usuários criados pelo admin.
# =====================================================================

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_created_by", "created_by"),
    )

    id_user: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    id_role: Mapped[int] = mapped_column(ForeignKey("roles.id_role"), nullable=False)
    # Nullable: o admin raiz não possui criador (bootstrap da base)
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id_user", ondelete="SET NULL"), nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    role: Mapped["Role"] = relationship(back_populates="users")
    creator: Mapped["User | None"] = relationship(
        remote_side=[id_user], back_populates="created_users"
    )
    created_users: Mapped[list["User"]] = relationship(back_populates="creator")

    def __repr__(self) -> str:
        return f"<User id={self.id_user} email={self.email!r}>"


# =====================================================================
# BREED (raca -> breeds). Tabela geral, acessível a todos os usuários.
# =====================================================================

class Breed(Base):
    __tablename__ = "breeds"
    __table_args__ = (
        UniqueConstraint("name", "species", name="uq_breeds_name_species"),
    )

    id_breed: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    species: Mapped[Species] = mapped_column(
        SAEnum(Species, name="species_enum"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    animals: Mapped[list["Animal"]] = relationship(back_populates="breed")

    def __repr__(self) -> str:
        return f"<Breed id={self.id_breed} name={self.name!r}>"


# =====================================================================
# OWNER (tutores -> owners). Cadastro simples do tutor do animal.
# =====================================================================

class Owner(Base):
    __tablename__ = "owners"
    __table_args__ = (
        Index("ix_owners_registered_by", "registered_by"),
        Index("ix_owners_national_id", "national_id"),
    )

    id_owner: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    national_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    registered_by: Mapped[int] = mapped_column(
        ForeignKey("users.id_user", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    registered_by_user: Mapped["User"] = relationship(foreign_keys=[registered_by])
    animals: Mapped[list["Animal"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan", passive_deletes=True
    )
    collections: Mapped[list["Collection"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Owner id={self.id_owner} name={self.name!r}>"


# =====================================================================
# VETERINARIAN (veterinarios -> veterinarians)
# =====================================================================

class Veterinarian(Base):
    __tablename__ = "veterinarians"

    id_veterinarian: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    license_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    vaccines: Mapped[list["Vaccine"]] = relationship(back_populates="veterinarian")
    exams: Mapped[list["Exam"]] = relationship(back_populates="veterinarian")
    collection_links: Mapped[list["CollectionVeterinarian"]] = relationship(
        back_populates="veterinarian", cascade="all, delete-orphan", passive_deletes=True
    )
    collection_animal_links: Mapped[list["CollectionAnimalVeterinarian"]] = relationship(
        back_populates="veterinarian", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Veterinarian id={self.id_veterinarian} name={self.name!r}>"


# =====================================================================
# ANIMAL (animal -> animals). 1 owner -> N animals | 1 animal -> 1 owner
# =====================================================================

class Animal(Base):
    __tablename__ = "animals"
    __table_args__ = (
        Index("ix_animals_owner", "id_owner"),
        Index("ix_animals_breed", "id_breed"),
        Index("ix_animals_registered_by", "registered_by"),
    )

    id_animal: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    species: Mapped[Species] = mapped_column(
        SAEnum(Species, name="species_enum"), nullable=False
    )
    id_breed: Mapped[int | None] = mapped_column(
        ForeignKey("breeds.id_breed", ondelete="SET NULL"), nullable=True
    )
    id_owner: Mapped[int] = mapped_column(
        ForeignKey("owners.id_owner", ondelete="CASCADE"), nullable=False
    )
    sex: Mapped[Sex] = mapped_column(SAEnum(Sex, name="sex_enum"), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    age_years: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    blood_type: Mapped[str] = mapped_column(String(10), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    registered_by: Mapped[int] = mapped_column(
        ForeignKey("users.id_user", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    breed: Mapped["Breed | None"] = relationship(back_populates="animals")
    owner: Mapped["Owner"] = relationship(back_populates="animals")
    registered_by_user: Mapped["User"] = relationship(foreign_keys=[registered_by])

    vaccines: Mapped[list["Vaccine"]] = relationship(
        back_populates="animal", cascade="all, delete-orphan", passive_deletes=True
    )
    exams: Mapped[list["Exam"]] = relationship(
        back_populates="animal", cascade="all, delete-orphan", passive_deletes=True
    )
    collection_links: Mapped[list["CollectionAnimal"]] = relationship(
        back_populates="animal", cascade="all, delete-orphan", passive_deletes=True
    )
    collection_vet_links: Mapped[list["CollectionAnimalVeterinarian"]] = relationship(
        back_populates="animal", cascade="all, delete-orphan", passive_deletes=True
    )
    blood_bag: Mapped["BloodBag | None"] = relationship(
        back_populates="animal", uselist=False, cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Animal id={self.id_animal} name={self.name!r}>"


# =====================================================================
# VACCINE (vacina -> vaccines). CRUD por animal.
# =====================================================================

class Vaccine(Base):
    __tablename__ = "vaccines"
    __table_args__ = (
        Index("ix_vaccines_animal", "id_animal"),
        Index("ix_vaccines_veterinarian", "id_veterinarian"),
        Index("ix_vaccines_application_date", "application_date"),
    )

    id_vaccine: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_animal: Mapped[int] = mapped_column(
        ForeignKey("animals.id_animal", ondelete="CASCADE"), nullable=False
    )
    vaccine_name: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    batch_number: Mapped[str] = mapped_column(String(50), nullable=False)
    application_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_dose_date: Mapped[date] = mapped_column(Date, nullable=False)
    id_veterinarian: Mapped[int] = mapped_column(
        ForeignKey("veterinarians.id_veterinarian"), nullable=False
    )
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    registered_by: Mapped[int] = mapped_column(
        ForeignKey("users.id_user", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    animal: Mapped["Animal"] = relationship(back_populates="vaccines")
    veterinarian: Mapped["Veterinarian"] = relationship(back_populates="vaccines")
    registered_by_user: Mapped["User"] = relationship(foreign_keys=[registered_by])

    def __repr__(self) -> str:
        return f"<Vaccine id={self.id_vaccine} name={self.vaccine_name!r}>"


# =====================================================================
# EXAM (exame/exames consolidados -> exams). Prévia rápida.
# =====================================================================

class Exam(Base):
    __tablename__ = "exams"
    __table_args__ = (
        Index("ix_exams_animal", "id_animal"),
        Index("ix_exams_veterinarian", "id_veterinarian"),
        Index("ix_exams_date", "exam_date"),
    )

    id_exam: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_animal: Mapped[int] = mapped_column(
        ForeignKey("animals.id_animal", ondelete="CASCADE"), nullable=False
    )
    id_veterinarian: Mapped[int | None] = mapped_column(
        ForeignKey("veterinarians.id_veterinarian", ondelete="SET NULL"), nullable=True
    )
    exam_type: Mapped[str] = mapped_column(String(100), nullable=False)
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ExamStatus] = mapped_column(
        SAEnum(ExamStatus, name="exam_status_enum"),
        nullable=False,
        default=ExamStatus.REQUESTED,
    )
    registered_by: Mapped[int] = mapped_column(
        ForeignKey("users.id_user", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    animal: Mapped["Animal"] = relationship(back_populates="exams")
    veterinarian: Mapped["Veterinarian | None"] = relationship(back_populates="exams")
    registered_by_user: Mapped["User"] = relationship(foreign_keys=[registered_by])
    detail: Mapped["ExamDetail | None"] = relationship(
        back_populates="exam", uselist=False, cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Exam id={self.id_exam} type={self.exam_type!r}>"


# =====================================================================
# EXAM_DETAIL (exame_detalhes -> exam_details). Relação 1:1 com exams.
# =====================================================================

class ExamDetail(Base):
    __tablename__ = "exam_details"

    id_exam_detail: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_exam: Mapped[int] = mapped_column(
        ForeignKey("exams.id_exam", ondelete="CASCADE"), nullable=False, unique=True
    )
    full_report: Mapped[str] = mapped_column(Text, nullable=False)
    reference_values: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[ExamResult] = mapped_column(
        SAEnum(ExamResult, name="exam_result_enum"), nullable=False
    )
    attachment_file: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    exam: Mapped["Exam"] = relationship(back_populates="detail")

    def __repr__(self) -> str:
        return f"<ExamDetail id={self.id_exam_detail} exam_id={self.id_exam}>"


# =====================================================================
# COLLECTION (coletas -> collections). Trimestral, por owner.
# =====================================================================

class Collection(Base):
    __tablename__ = "collections"
    __table_args__ = (
        Index("ix_collections_owner", "id_owner"),
        Index("ix_collections_date", "collection_date"),
    )

    id_collection: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_owner: Mapped[int] = mapped_column(
        ForeignKey("owners.id_owner", ondelete="CASCADE"), nullable=False
    )
    collection_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Sincronizado por lógica de aplicação (evento SQLAlchemy) a partir de collection_animals
    animal_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    registered_by: Mapped[int] = mapped_column(
        ForeignKey("users.id_user", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    owner: Mapped["Owner"] = relationship(back_populates="collections")
    registered_by_user: Mapped["User"] = relationship(foreign_keys=[registered_by])

    animal_links: Mapped[list["CollectionAnimal"]] = relationship(
        back_populates="collection", cascade="all, delete-orphan", passive_deletes=True
    )
    veterinarian_links: Mapped[list["CollectionVeterinarian"]] = relationship(
        back_populates="collection", cascade="all, delete-orphan", passive_deletes=True
    )
    animal_veterinarian_links: Mapped[list["CollectionAnimalVeterinarian"]] = relationship(
        back_populates="collection", cascade="all, delete-orphan", passive_deletes=True
    )
    blood_bag: Mapped["BloodBag | None"] = relationship(back_populates="collection", uselist=False)

    def __repr__(self) -> str:
        return f"<Collection id={self.id_collection} date={self.collection_date}>"


# =====================================================================
# COLLECTION_ANIMAL (coleta_animais -> collection_animals). PK composta.
# =====================================================================

class CollectionAnimal(Base):
    __tablename__ = "collection_animals"

    id_collection: Mapped[int] = mapped_column(
        ForeignKey("collections.id_collection", ondelete="CASCADE"), primary_key=True
    )
    id_animal: Mapped[int] = mapped_column(
        ForeignKey("animals.id_animal", ondelete="CASCADE"), primary_key=True
    )

    collection: Mapped["Collection"] = relationship(back_populates="animal_links")
    animal: Mapped["Animal"] = relationship(back_populates="collection_links")

    def __repr__(self) -> str:
        return f"<CollectionAnimal collection={self.id_collection} animal={self.id_animal}>"


# =====================================================================
# COLLECTION_VETERINARIAN (coleta_veterinarios -> collection_veterinarians)
# PK composta.
# =====================================================================

class CollectionVeterinarian(Base):
    __tablename__ = "collection_veterinarians"

    id_collection: Mapped[int] = mapped_column(
        ForeignKey("collections.id_collection", ondelete="CASCADE"), primary_key=True
    )
    id_veterinarian: Mapped[int] = mapped_column(
        ForeignKey("veterinarians.id_veterinarian", ondelete="CASCADE"), primary_key=True
    )

    collection: Mapped["Collection"] = relationship(back_populates="veterinarian_links")
    veterinarian: Mapped["Veterinarian"] = relationship(back_populates="collection_links")

    def __repr__(self) -> str:
        return f"<CollectionVeterinarian collection={self.id_collection} vet={self.id_veterinarian}>"


# =====================================================================
# COLLECTION_ANIMAL_VETERINARIAN
# (coleta_animal_veterinario -> collection_animal_veterinarian)
# Qual veterinário coletou de qual animal.
# =====================================================================

class CollectionAnimalVeterinarian(Base):
    __tablename__ = "collection_animal_veterinarian"
    __table_args__ = (
        UniqueConstraint("id_collection", "id_animal", name="uq_collection_animal_vet"),
        Index("ix_cav_collection", "id_collection"),
        Index("ix_cav_animal", "id_animal"),
        Index("ix_cav_veterinarian", "id_veterinarian"),
    )

    id_collection_animal_vet: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_collection: Mapped[int] = mapped_column(
        ForeignKey("collections.id_collection", ondelete="CASCADE"), nullable=False
    )
    id_animal: Mapped[int] = mapped_column(
        ForeignKey("animals.id_animal", ondelete="CASCADE"), nullable=False
    )
    id_veterinarian: Mapped[int] = mapped_column(
        ForeignKey("veterinarians.id_veterinarian", ondelete="CASCADE"), nullable=False
    )
    collection_time: Mapped[time] = mapped_column(Time, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)

    collection: Mapped["Collection"] = relationship(back_populates="animal_veterinarian_links")
    animal: Mapped["Animal"] = relationship(back_populates="collection_vet_links")
    veterinarian: Mapped["Veterinarian"] = relationship(back_populates="collection_animal_links")

    def __repr__(self) -> str:
        return (
            f"<CollectionAnimalVeterinarian collection={self.id_collection} "
            f"animal={self.id_animal} vet={self.id_veterinarian}>"
        )


# =====================================================================
# BLOOD_BAG (bolsas_sangue -> blood_bags). 1:1 com animal e com coleta.
# =====================================================================

class BloodBag(Base):
    __tablename__ = "blood_bags"
    __table_args__ = (
        Index("ix_blood_bags_animal", "id_animal"),
        Index("ix_blood_bags_collection", "id_collection"),
    )

    id_blood_bag: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hash_code: Mapped[str] = mapped_column(String(255), nullable=False)
    blood_type: Mapped[str] = mapped_column(String(10), nullable=False)
    id_animal: Mapped[int] = mapped_column(
        ForeignKey("animals.id_animal", ondelete="CASCADE"), nullable=False, unique=True
    )
    id_collection: Mapped[int | None] = mapped_column(
        ForeignKey("collections.id_collection", ondelete="SET NULL"), nullable=True, unique=True
    )
    notes: Mapped[str] = mapped_column(String(255), nullable=False)
    volume_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    collection_date: Mapped[date] = mapped_column(Date, nullable=False)
    sale_date: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    animal: Mapped["Animal"] = relationship(back_populates="blood_bag")
    collection: Mapped["Collection | None"] = relationship(back_populates="blood_bag")

    def __repr__(self) -> str:
        return f"<BloodBag id={self.id_blood_bag} animal={self.id_animal}>"


# =====================================================================
# INFRAESTRUTURA DE BANCO DE DADOS (MYSQL CONFIGURED)
# =====================================================================

# Exemplo de URL de Conexão MySQL: mysql+pymysql://<usuario>:<senha>@<host>:<porta>/<banco>
# É recomendado que altere os valores abaixo para bater com as credenciais do seu servidor MySQL local/produção.
DATABASE_URL = os.getenv("DATABASE_URL")


class Database:
    def __init__(self, database_url: str = DATABASE_URL):
        self.engine = create_engine(
            database_url,
            pool_recycle=3600,  # Evita erro de desconexão inativa do MySQL (limite de 8h)
            pool_pre_ping=True,  # Executa um teste "ping" simples antes de reutilizar uma conexão do pool
            echo=False           # Altere para True caso queira debugar as queries SQL enviadas ao MySQL
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )

        # Cria as tabelas do MySQL fisicamente, se estas ainda não existirem
        Base.metadata.create_all(bind=self.engine)

    # Retorna uma nova sessão local do banco de dados
    def get_session(self):
        return self.SessionLocal()