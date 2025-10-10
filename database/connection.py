from sqlalchemy import (
    create_engine,
    Column,
    String,
    DateTime,
    Boolean,
    Date,
    Text,
    ForeignKey,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

connection_string = os.getenv("DATABASE_URL")
if not connection_string:
    raise ValueError("DATABASE_URL environment variable is not set.")
engine = create_engine(
    connection_string, echo=True, pool_pre_ping=True, pool_recycle=300
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(name={self.name})>"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100))
    password = Column(String(255), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    is_deleted = Column(Boolean, default=False)

    role = relationship("Role", back_populates="users")
    loans = relationship("Loan", foreign_keys="Loan.user_id", back_populates="user")

    def __repr__(self):
        return f"<User(email={self.email})>"


class Author(Base):
    __tablename__ = "authors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    nationality = Column(String(50))
    birth_date = Column(Date)
    death_date = Column(Date)
    biography = Column(Text)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    materials = relationship("Material", back_populates="author")

    def __repr__(self):
        return f"<Author(name={self.name})>"


class MaterialType(Base):
    __tablename__ = "material_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    materials = relationship("Material", back_populates="material_type")

    def __repr__(self):
        return f"<MaterialType(name={self.name})>"


class Material(Base):
    __tablename__ = "materials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("authors.id"), nullable=False)
    type_id = Column(UUID(as_uuid=True), ForeignKey("material_types.id"), nullable=False)
    is_deleted = Column(Boolean, default=False)
    date_added = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    author = relationship("Author", back_populates="materials")
    material_type = relationship("MaterialType", back_populates="materials")
    loans = relationship(
        "Loan", foreign_keys="Loan.material_id", back_populates="material"
    )

    def __repr__(self):
        return f"<Material(title={self.title})>"


class LoanStatus(Base):
    __tablename__ = "loan_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    loans = relationship("Loan", back_populates="status")

    def __repr__(self):
        return f"<LoanStatus(name={self.name})>"


class Loan(Base):
    __tablename__ = "loans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    material_id = Column(UUID(as_uuid=True), ForeignKey("materials.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    loan_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expected_return_date = Column(DateTime, nullable=False)
    actual_return_date = Column(DateTime)
    status_id = Column(UUID(as_uuid=True), ForeignKey("loan_status.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    material = relationship("Material", back_populates="loans")
    user = relationship("User", foreign_keys="Loan.user_id", back_populates="loans")
    status = relationship("LoanStatus", back_populates="loans")

    def __repr__(self):
        return f"<Loan(user_id={self.user_id}, material_id={self.material_id})>"


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente.")


def migrate_database():
    Base.metadata.create_all(bind=engine)

    # Configurar el hash de contraseñas
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    with SessionLocal() as db:
        # Crear roles si no existen
        if db.query(Role).count() == 0:
            admin_role = Role(
                name="admin",
                description="Administrador del sistema"
            )
            client_role = Role(
                name="cliente",
                description="Cliente de la biblioteca"
            )
            db.add_all([admin_role, client_role])
            db.commit()
            print("👥 Roles de ejemplo insertados.")
        else:
            admin_role = db.query(Role).filter_by(name="admin").first()
            client_role = db.query(Role).filter_by(name="cliente").first()
            print("⚠️ Ya existen roles, no se insertaron de nuevo.")

        # Crear usuarios si no existen
        if db.query(User).count() == 0:
            admin = User(
                email="admin@ejemplo.com",
                full_name="Administrador",
                password=pwd_context.hash("admin123"),
                role_id=admin_role.id,
            )
            user1 = User(
                email="usuario1@ejemplo.com",
                full_name="Juan Pérez",
                password=pwd_context.hash("user123"),
                role_id=client_role.id,
            )
            db.add_all([admin, user1])
            db.commit()
            print("👤 Usuarios de ejemplo insertados.")

            admin_id = admin.id
            user1_id = user1.id

        else:
            admin_id = db.query(User.id).filter_by(email="admin@ejemplo.com").scalar()
            user1_id = (
                db.query(User.id).filter_by(email="usuario1@ejemplo.com").scalar()
            )
            print("⚠️ Ya existen usuarios, no se insertaron de nuevo.")

        # Crear autores si no existen
        if db.query(Author).count() == 0:
            author1 = Author(
                name="Antoine de Saint-Exupéry",
                nationality="Francés",
                birth_date="1900-06-29"
            )
            author2 = Author(
                name="Miguel de Cervantes",
                nationality="Español",
                birth_date="1547-09-29",
                death_date="1616-04-22"
            )
            db.add_all([author1, author2])
            db.commit()
            print("✍️ Autores de ejemplo insertados.")
        else:
            author1 = db.query(Author).filter_by(name="Antoine de Saint-Exupéry").first()
            author2 = db.query(Author).filter_by(name="Miguel de Cervantes").first()
            print("⚠️ Ya existen autores, no se insertaron de nuevo.")

        # Crear tipos de material si no existen
        if db.query(MaterialType).count() == 0:
            book_type = MaterialType(
                name="book",
                description="Libro"
            )
            magazine_type = MaterialType(
                name="magazine",
                description="Revista"
            )
            newspaper_type = MaterialType(
                name="newspaper",
                description="Periódico"
            )
            db.add_all([book_type, magazine_type, newspaper_type])
            db.commit()
            print("📖 Tipos de material de ejemplo insertados.")
        else:
            book_type = db.query(MaterialType).filter_by(name="book").first()
            magazine_type = db.query(MaterialType).filter_by(name="magazine").first()
            newspaper_type = db.query(MaterialType).filter_by(name="newspaper").first()
            print("⚠️ Ya existen tipos de material, no se insertaron de nuevo.")

        # Crear materiales si no existen
        if db.query(Material).count() == 0:
            m1 = Material(
                title="El Principito",
                author_id=author1.id,
                type_id=book_type.id,
                created_by=admin_id,
                updated_by=admin_id,
            )
            m2 = Material(
                title="Don Quijote",
                author_id=author2.id,
                type_id=book_type.id,
                created_by=admin_id,
                updated_by=admin_id,
            )
            db.add_all([m1, m2])
            db.commit()
            print("📚 Materiales de ejemplo insertados.")
            m1_id = m1.id
            m2_id = m2.id
        else:
            m1_id = db.query(Material.id).filter_by(title="El Principito").scalar()
            m2_id = db.query(Material.id).filter_by(title="Don Quijote").scalar()
            print("⚠️ Ya existen materiales, no se insertaron de nuevo.")

        # Crear estados de préstamo si no existen
        if db.query(LoanStatus).count() == 0:
            borrowed_status = LoanStatus(name="borrowed")
            returned_status = LoanStatus(name="returned")
            overdue_status = LoanStatus(name="overdue")
            db.add_all([borrowed_status, returned_status, overdue_status])
            db.commit()
            print("📋 Estados de préstamo insertados.")
        else:
            borrowed_status = db.query(LoanStatus).filter_by(name="borrowed").first()
            returned_status = db.query(LoanStatus).filter_by(name="returned").first()
            overdue_status = db.query(LoanStatus).filter_by(name="overdue").first()
            print("⚠️ Ya existen estados de préstamo, no se insertaron de nuevo.")

        # Crear préstamos si no existen
        if db.query(Loan).count() == 0:
            loan1 = Loan(
                material_id=m1_id,
                user_id=user1_id,
                expected_return_date=datetime.now(timezone.utc),
                status_id=borrowed_status.id,
                created_by=admin_id,
                updated_by=admin_id,
            )
            loan2 = Loan(
                material_id=m2_id,
                user_id=admin_id,
                expected_return_date=datetime.now(timezone.utc),
                status_id=returned_status.id,
                actual_return_date=datetime.now(timezone.utc),
                created_by=admin_id,
                updated_by=admin_id,
            )
            db.add_all([loan1, loan2])
            db.commit()
            print("📋 Préstamos de ejemplo insertados.")
        else:
            print("⚠️ Ya existen préstamos, no se insertaron de nuevo.")

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
