from sqlalchemy import (
    create_engine,
    Column,
    String,
    DateTime,
    Boolean,
    Enum,
    ForeignKey,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from common import MaterialType
from uuid import uuid4

load_dotenv()

connection_string = os.getenv("SQL_SERVER_CONNECTION_STRING")
if not connection_string:
    raise ValueError("SQL_SERVER_CONNECTION_STRING environment variable is not set.")
engine = create_engine(
    connection_string, echo=True, pool_pre_ping=True, pool_recycle=300
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100))
    password = Column(String(255), nullable=False)
    rol = Column(String(20), default="cliente")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(String(36), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by = Column(String(36), nullable=True)
    is_deleted = Column(Boolean, default=False)

    loans = relationship("Loan", foreign_keys="Loan.user_id", back_populates="user")

    def __repr__(self):
        return f"<User( email={self.email})>"


class Material(Base):
    __tablename__ = "materials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    type = Column(Enum(MaterialType, name="material_type_enum"), nullable=False)
    is_deleted = Column(Boolean, default=False)
    date_added = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(String(36), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by = Column(String(36), nullable=True)

    loans = relationship(
        "Loan", foreign_keys="Loan.material_id", back_populates="material"
    )

    def __repr__(self):
        return f"<Material(title={self.title}, author={self.author}, type={self.type})>"


class Loan(Base):
    __tablename__ = "loans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    material_id = Column(String(36), ForeignKey("materials.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    loan_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expected_return_date = Column(DateTime, nullable=False)
    actual_return_date = Column(DateTime)
    is_returned = Column(Boolean, default=False)
    created_by = Column(String(36), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by = Column(String(36), nullable=True)

    material = relationship("Material", back_populates="loans")
    user = relationship("User", foreign_keys="Loan.user_id", back_populates="loans")

    def __repr__(self):
        return f"<Loan(user_id={self.user_id}, material_id={self.material_id}, returned={self.is_returned})>"


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente.")


def migrate_database():
    Base.metadata.create_all(bind=engine)

    # Configurar el hash de contraseñas
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    with SessionLocal() as db:
        if db.query(User).count() == 0:
            admin = User(
                email="admin@ejemplo.com",
                full_name="Administrador",
                password=pwd_context.hash("admin123"),
                rol="admin",
                id=str(uuid4()),
            )
            user1 = User(
                email="usuario1@ejemplo.com",
                full_name="Juan Pérez",
                password=pwd_context.hash("user123"),
                rol="cliente",
                id=str(uuid4()),
            )
            db.add_all([admin, user1])
            print("👤 Usuarios de ejemplo insertados.")

            admin_id = admin.id
            user1_id = user1.id

        else:
            admin_id = db.query(User.id).filter_by(email="admin@ejemplo.com").scalar()
            user1_id = (
                db.query(User.id).filter_by(email="usuario1@ejemplo.com").scalar()
            )
            print("⚠️ Ya existen usuarios, no se insertaron de nuevo.")

        if db.query(Material).count() == 0:
            m1 = Material(
                title="El Principito",
                author="Antoine de Saint-Exupéry",
                type="book",
                created_by=admin_id,
                updated_by=admin_id,
                id=str(uuid4()),
            )
            m2 = Material(
                title="Don Quijote",
                author="Miguel de Cervantes",
                type="book",
                created_by=admin_id,
                updated_by=admin_id,
                id=str(uuid4()),
            )
            db.add_all([m1, m2])
            print("📚 Materiales de ejemplo insertados.")
            m1_id = m1.id
            m2_id = m2.id
        else:
            m1_id = db.query(Material.id).filter_by(title="El Principito").scalar()
            m2_id = db.query(Material.id).filter_by(title="Don Quijote").scalar()
            print("⚠️ Ya existen materiales, no se insertaron de nuevo.")

        if db.query(Loan).count() == 0:
            loan1 = Loan(
                material_id=m1_id,
                user_id=user1_id,
                expected_return_date=datetime.now(timezone.utc),
                created_by=admin_id,
                updated_by=admin_id,
                id=str(uuid4()),
            )
            loan2 = Loan(
                material_id=m2_id,
                user_id=admin_id,
                expected_return_date=datetime.now(timezone.utc),
                created_by=admin_id,
                updated_by=admin_id,
                id=str(uuid4()),
            )
            db.add_all([loan1, loan2])
            print("Prestamos de ejemplo insertados.")
        else:
            print("⚠️ Ya existen prestamos, no se insertaron de nuevo.")

        db.commit()

    print("✅ Migración ejecutada correctamente.")


def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✅ Conexión exitosa.")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


if __name__ == "__main__":
    print("🔄 Probando conexión a la base de datos...")
    if test_connection():
        migrate_database()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
