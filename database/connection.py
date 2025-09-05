from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv
from common import MaterialType

load_dotenv()

connection_string = os.getenv('SQL_SERVER_CONNECTION_STRING')
engine = create_engine(connection_string, echo=True, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100))
    password = Column(String(255), nullable=False)
    rol = Column(String(20), default="cliente")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    loans = relationship("Loan", back_populates="user")

    def __repr__(self):
        return f"<User( email={self.email})>"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    type = Column(Enum(MaterialType, name="material_type_enum"), nullable=False)
    is_deleted = Column(Boolean, default=False)
    date_added = Column(DateTime, default=datetime.utcnow)

    loans = relationship("Loan", back_populates="material")

    def __repr__(self):
        return f"<Material(title={self.title}, author={self.author}, type={self.type})>"

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    loan_date = Column(DateTime, default=datetime.utcnow)
    expected_return_date = Column(DateTime, nullable=False)
    actual_return_date = Column(DateTime)
    is_returned = Column(Boolean, default=False)

    material = relationship("Material", back_populates="loans")
    user = relationship("User", back_populates="loans")

    def __repr__(self):
        return f"<Loan(user_id={self.user_id}, material_id={self.material_id}, returned={self.is_returned})>"


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente.")


def migrate_database():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        if db.query(User).count() == 0:
            admin = User(
                email="admin@ejemplo.com",
                full_name="Administrador",
                password="hashed_password",
                rol="admin"
            )
            user1 = User(
                email="usuario1@ejemplo.com",
                full_name="Juan Pérez",
                password="hashed_password",
                rol="cliente"
            )
            db.add_all([admin, user1])
            print("👤 Usuarios de ejemplo insertados.")
        else:
            print("⚠️ Ya existen usuarios, no se insertaron de nuevo.")

        if db.query(Material).count() == 0:
            m1 = Material(title="El Principito", author="Antoine de Saint-Exupéry", type="book")
            m2 = Material(title="Don Quijote", author="Miguel de Cervantes", type="book")
            db.add_all([m1, m2])
            print("📚 Materiales de ejemplo insertados.")
        else:
            print("⚠️ Ya existen materiales, no se insertaron de nuevo.")

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