from database.connection import db
from models.schemas import Base
from sqlalchemy import text

def migrate_database():
    """Migra la base de datos usando SQL directo"""
    
    # Scripts SQL para crear las tablas
    create_users_table = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
    BEGIN
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username NVARCHAR(50) UNIQUE NOT NULL,
            email NVARCHAR(100) UNIQUE NOT NULL,
            full_name NVARCHAR(100),
            password NVARCHAR(255) NOT NULL,
            rol NVARCHAR(20) DEFAULT 'cliente' CHECK (rol IN ('cliente', 'admin')),
            created_at DATETIME2 DEFAULT GETDATE(),
            is_deleted BIT DEFAULT 0
        )
        
        -- Crear índices para mejor rendimiento
        CREATE INDEX IX_users_username ON users(username)
        CREATE INDEX IX_users_email ON users(email)
        CREATE INDEX IX_users_rol ON users(rol)
        CREATE INDEX IX_users_is_deleted ON users(is_deleted)
        
        PRINT 'Tabla users creada exitosamente'
    END
    ELSE
    BEGIN
        PRINT 'Tabla users ya existe'
    END
    """
    
    create_materials_table = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='materials' AND xtype='U')
    BEGIN
        CREATE TABLE materials (
            id INT IDENTITY(1,1) PRIMARY KEY,
            title NVARCHAR(200) NOT NULL,
            author NVARCHAR(100) NOT NULL,
            type NVARCHAR(50) NOT NULL,
            is_deleted BIT DEFAULT 0,
            date_added DATETIME2 DEFAULT GETDATE()
        )
        
        CREATE INDEX IX_materials_type ON materials(type)
        CREATE INDEX IX_materials_author ON materials(author)
        CREATE INDEX IX_materials_date_added ON materials(date_added)
        CREATE INDEX IX_materials_is_deleted ON materials(is_deleted)
        
        PRINT 'Tabla materials creada exitosamente'
    END
    ELSE
    BEGIN
        PRINT 'Tabla materials ya existe'
    END
    """
    
    create_loans_table = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='loans' AND xtype='U')
    BEGIN
        CREATE TABLE loans (
            id INT IDENTITY(1,1) PRIMARY KEY,
            material_id INT NOT NULL,
            user_id INT NOT NULL,
            loan_date DATETIME2 DEFAULT GETDATE(),
            expected_return_date DATETIME2 NOT NULL,
            actual_return_date DATETIME2,
            is_returned BIT DEFAULT 0,
            FOREIGN KEY (material_id) REFERENCES materials(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        
        CREATE INDEX IX_loans_material_id ON loans(material_id)
        CREATE INDEX IX_loans_user_id ON loans(user_id)
        CREATE INDEX IX_loans_loan_date ON loans(loan_date)
        CREATE INDEX IX_loans_expected_return_date ON loans(expected_return_date)
        CREATE INDEX IX_loans_actual_return_date ON loans(actual_return_date)
        CREATE INDEX IX_loans_is_returned ON loans(is_returned)
        
        PRINT 'Tabla loans creada exitosamente'
    END
    ELSE
    BEGIN
        PRINT 'Tabla loans ya existe'
    END
    """
    
    # Scripts para insertar datos de ejemplo
    insert_sample_users = """
    IF NOT EXISTS (SELECT * FROM users WHERE username = 'admin')
    BEGIN
        INSERT INTO users (username, email, full_name, password, rol, is_deleted)
        VALUES 
            ('admin', 'admin@ejemplo.com', 'Administrador del Sistema', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'admin', 0),
            ('usuario1', 'usuario1@ejemplo.com', 'Juan Pérez', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'cliente', 0),
            ('maria_garcia', 'maria@ejemplo.com', 'María García', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'cliente', 0),
            ('bibliotecario', 'biblio@ejemplo.com', 'Carlos López', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'admin', 0)
        
        PRINT 'Usuarios de ejemplo insertados'
    END
    ELSE
    BEGIN
        PRINT 'Usuarios de ejemplo ya existen'
    END
    """
    
    insert_sample_materials = """
    IF NOT EXISTS (SELECT * FROM materials WHERE title = 'El Principito')
    BEGIN
        INSERT INTO materials (title, author, type, is_deleted, date_added)
        VALUES 
            ('El Principito', 'Antoine de Saint-Exupéry', 'book', 0, '2024-01-15T10:30:00'),
            ('Don Quijote', 'Miguel de Cervantes', 'book', 0, '2024-01-16T14:20:00'),
            ('National Geographic', 'Varios Autores', 'magazine', 0, '2024-01-17T09:15:00'),
            ('El País', 'Varios Autores', 'newspaper', 0, '2024-01-18T07:00:00')
        
        PRINT 'Materiales de ejemplo insertados'
    END
    ELSE
    BEGIN
        PRINT 'Materiales de ejemplo ya existen'
    END
    """
    
    try:
        print("Iniciando migración de la base de datos...")
        
        # Ejecutar scripts de creación de tablas
        db.execute_non_query(create_users_table)
        db.execute_non_query(create_materials_table)
        db.execute_non_query(create_loans_table)
        
        # Insertar datos de ejemplo
        db.execute_non_query(insert_sample_users)
        db.execute_non_query(insert_sample_materials)
        
        print("Migración completada exitosamente!")
        
    except Exception as e:
        print(f"Error durante la migración: {e}")
        raise

if __name__ == "__main__":
    migrate_database()
