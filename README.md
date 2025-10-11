# Sistema de Biblioteca - API REST

## Descripción General
Desarrollo de una API REST completa para un sistema de biblioteca donde puedes gestionar libros, revistas y periódicos.

La API te permite hacer las operaciones típicas de una biblioteca:
- **Gestionar materiales**: Agregar, ver, editar y eliminar libros, revistas y periódicos
- **Operaciones de préstamo**: Prestar y devolver materiales
- **Búsquedas**: Encontrar todos los materiales o por autor
- **Gestión de usuarios**: Administrar usuarios del sistema con roles (cliente/admin)
- **Control de acceso**: Diferentes permisos según el rol del usuario

## Características

- **FastAPI**: Framework moderno y rápido para APIs con Python
- **SQLAlchemy**: ORM robusto para manejo de base de datos
- **PostgreSQL**: Base de datos relacional robusta y escalable
- **CRUD Completo**: Operaciones Create, Read, Update y Delete
- **Sistema de Roles**: Control de acceso basado en roles (cliente/admin)
- **Validación de Datos**: Con Pydantic para esquemas robustos
- **Documentación Automática**: Swagger UI integrado
- **Manejo de Errores**: Respuestas HTTP apropiadas
- **Soft Delete**: Opción de eliminar sin perder datos
- **CORS**: Configurado para desarrollo frontend
- **Migración Automática**: Base de datos se configura automáticamente

## Arquitectura del Proyecto

```
SistemaDeBiblioteca/
├── common/
│   └── enums/                 # Enumeraciones compartidas (roles, estados, etc.)
├── database/
│   └── connection.py          # Configuración de SQLAlchemy, conexión y migración
├── endpoints/
│   ├── loans/                 # Endpoints para préstamos
│   ├── materials/             # Endpoints para materiales
│   ├── users/                 # Endpoints para usuarios
│   └── __init__.py            # Inicialización del módulo de endpoints
├── models/
│   └── schemas.py             # Modelos Pydantic y SQLAlchemy
├── scripts/                   # Scripts utilitarios
│   └── migrate_database.py    # Script de migración de base de datos
├── venv/                      # Entorno virtual de Python
├── .env                       # Variables de entorno (credenciales, configuración)
├── .gitignore                 # Archivos ignorados por Git
├── config.py                  # Configuración general de la aplicación
├── main.py                    # Punto de entrada de la aplicación FastAPI
├── README.md                  # Documentación del proyecto
└── requirements.txt           # Dependencias del proyecto
```

### Descripción de la Estructura:

- **`database/`**: Configuración de base de datos y migraciones
- **`endpoints/`**: API endpoints organizados por módulos (loans, materials, users)
- **`models/`**: Esquemas de datos y validaciones
- **`scripts/`**: Scripts de migración y utilidades
- **`config.py`**: Configuración de la aplicación
- **`main.py`**: Punto de entrada de la aplicación FastAPI
- **`requirements.txt`**: Dependencias del proyecto

## Requisitos Previos

### Software Requerido
- **Python 3.8+**
- **PostgreSQL 12+**
- **psycopg2** (driver de PostgreSQL para Python)

### Instalación de PostgreSQL
1. Descarga PostgreSQL desde [postgresql.org](https://www.postgresql.org/download/)
2. Instala según tu sistema operativo
3. Configura usuario y contraseña durante la instalación
4. Verifica la instalación ejecutando `psql --version`

## Instalación

### 1. Clonar o Descargar el Proyecto
```bash
git clone https://github.com/JBernal27/SistemaDeBiblioteca.git
cd SistemaDeBiblioteca
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt #Si no funciona probar con " py -m " o " python -m "  antes 
```

### 4. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
# Configuración de la base de datos PostgreSQL
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/SistemaDeBiblioteca

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Desarrollo
DEBUG=true
RELOAD=true

# Logging
LOG_LEVEL=debug

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Seguridad
SECRET_KEY = "secretito123"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES=30
```

### 5. Configurar Base de Datos
1. Abre pgAdmin o conecta via línea de comandos
2. Conéctate a tu instancia de PostgreSQL
3. Crea una nueva base de datos llamada `SistemaDeBiblioteca`

```sql
-- Crear la base de datos
CREATE DATABASE SistemaDeBiblioteca;
```

## Ejecución

### Opción 1: Ejecución Directa (Recomendado)
```bash
# Desde la carpeta SistemaDeBiblioteca
python main.py
```

### Opción 2: Con Uvicorn
```bash
# Desde la carpeta SistemaDeBiblioteca
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Opción 3: Con Uvicorn en Producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Migración Automática de Base de Datos

### ¿Qué Hace la Migración?

Al iniciar la API, automáticamente se ejecuta:

1. **Conexión a PostgreSQL**
2. **Creación de tablas** (si no existen)
3. **Migración de esquemas**
4. **Inserción de datos de ejemplo**

### Esquema de Base de Datos

El sistema utiliza las siguientes tablas según el diagrama ERD:

#### Tabla `roles`
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    description VARCHAR(200)
);
```

#### Tabla `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    password VARCHAR(255) NOT NULL,
    role_id UUID NOT NULL REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

#### Tabla `authors`
```sql
CREATE TABLE authors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    nationality VARCHAR(50),
    birth_date DATE,
    death_date DATE,
    biography TEXT
);
```

#### Tabla `material_types`
```sql
CREATE TABLE material_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    description VARCHAR(200)
);
```

#### Tabla `materials`
```sql
CREATE TABLE materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    author_id UUID NOT NULL REFERENCES authors(id),
    type_id UUID NOT NULL REFERENCES material_types(id),
    is_deleted BOOLEAN DEFAULT FALSE,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla `loan_status`
```sql
CREATE TABLE loan_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL
);
```

#### Tabla `loans`
```sql
CREATE TABLE loans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID NOT NULL REFERENCES materials(id),
    user_id UUID NOT NULL REFERENCES users(id),
    loan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_return_date TIMESTAMP NOT NULL,
    actual_return_date TIMESTAMP,
    status_id UUID NOT NULL REFERENCES loan_status(id),
    created_by UUID,
    updated_by UUID,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Datos de Ejemplo Insertados

#### Usuarios
- **Administrador** - `admin@ejemplo.com` / contraseña: `admin123` / **Rol: Admin**
- **Juan Pérez** - `usuario1@ejemplo.com` / contraseña: `user123` / **Rol: Cliente**


#### Materiales
- **El Principito** - Antoine de Saint-Exupéry (Libro)
- **Don Quijote** - Miguel de Cervantes (Libro)
### Sistema de Roles

#### Rol: **Admin**
- Acceso completo a todas las funcionalidades
- Puede realizar préstamos de materiales
- Puede gestionar usuarios, materiales y préstamos
- Puede crear, editar y eliminar cualquier registro

#### Rol: **Cliente**
- Puede ver materiales disponibles
- Puede ver su historial de préstamos
- Control de fechas: Conocimiento de fechas de entrega esperadas

## Endpoints Disponibles

### Usuarios

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|----------------|
| `GET` | `/users` | Obtener lista paginada de usuarios | Admin |
| `GET` | `/users/{id}` | Obtener usuario específico por ID | Admin |
| `POST` | `/users` | Crear nuevo usuario | Admin |
| `PUT` | `/users/{id}` | Actualizar usuario existente | Admin |
| `DELETE` | `/users/{id}` | Eliminar usuario (soft delete) | Admin |

### Materiales

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|----------------|
| `GET` | `/materials` | Obtener lista de materiales disponibles | Cliente/Admin |
| `GET` | `/materials/{id}` | Obtener material específico | Cliente/Admin |
| `GET` | `/materials/search?autor=nombreAutor` | Buscar materiales por nombre de autor | Cliente/Admin |
| `POST` | `/materials` | Crear nuevo material | Admin |
| `PUT` | `/materials/{id}` | Actualizar material existente | Admin |
| `DELETE` | `/materials/{id}` | Eliminar material (soft delete) | Admin |

### Préstamos

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|----------------|
| `GET` | `/loans` | Obtener todos los préstamos | Admin |
| `PUT` | `/loans/{id}/return` | Registar devolucion | Admin |
| `POST` | `/loans` | Crear nuevo préstamo | Admin |
| `GET` | `/loans/my` | Obtener préstamos del usuario actual | Cliente |
| `GET` | `/loans/{id}` | Obtener préstamo específico | Admin |
| `GET` | `/loans/user/{id}` | Obtener préstamos de usuario específico | Admin |
| `PUT` | `/loans/{id}` | Actualizar préstamo existente | Admin |

### Endpoints del Sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/docs` | Documentación Swagger UI |

## Ejemplos de Uso

### Crear Usuario Cliente
```bash
curl -X POST "http://localhost:8000/users" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "juan@ejemplo.com",
       "full_name": "Juan Pérez",
       "password": "contraseña123",
       "rol": "cliente"
     }'
```

### Crear Usuario Administrador
```bash
curl -X POST "http://localhost:8000/users" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "biblio@biblioteca.com",
       "full_name": "Carlos López",
       "password": "admin123",
       "rol": "admin"
     }'
```

### Obtener Usuarios
```bash
curl "http://localhost:8000/users?skip=0&limit=10"
```

### Obtener Solo Administradores
```bash
curl "http://localhost:8000/users?rol=admin&skip=0&limit=10"
```

### Obtener Solo Clientes
```bash
curl "http://localhost:8000/users?rol=cliente&skip=0&limit=10"
```

### Actualizar Usuario
```bash
curl -X PUT "http://localhost:8000/users/1" \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Juan Carlos Pérez",
       "rol": "admin"
     }'
```

### Eliminar Usuario
```bash
curl -X DELETE "http://localhost:8000/users/1"
```

### Crear Material
```bash
curl -X POST "http://localhost:8000/materials" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Cien Años de Soledad",
       "author": "Gabriel García Márquez",
       "type": "book"
     }'
```

### Obtener Materiales
```bash
curl "http://localhost:8000/materials?type=book&skip=0&limit=10"
```

### Solicitar Préstamo (Cliente)
```bash
curl -X POST "http://localhost:8000/loans/request" \
     -H "Content-Type: application/json" \
     -d '{
       "material_id": 1,
       "expected_return_date": "2024-02-15T23:59:59"
     }'
```

### Crear Préstamo (Admin)
```bash
curl -X POST "http://localhost:8000/loans" \
     -H "Content-Type: application/json" \
     -d '{
       "material_id": 1,
       "user_id": 2,
       "expected_return_date": "2024-02-15T23:59:59"
     }'
```

### Devolver Material (Admin)
```bash
curl -X PUT "http://localhost:8000/loans/1" \
     -H "Content-Type: application/json" \
     -d '{
       "actual_return_date": "2024-02-10T14:30:00",
       "is_returned": true
     }'
```

### Ver Mis Préstamos (Cliente)
```bash
curl "http://localhost:8000/loans/my"
```

## Solución de Problemas

### Error: "Connection refused"
1. Verifica que PostgreSQL esté ejecutándose
2. Confirma que el puerto 5432 esté disponible
3. Verifica que el usuario y contraseña sean correctos
4. Asegúrate de que la base de datos exista

### Error: "Database does not exist"
1. Crea la base de datos `sistema_biblioteca` en PostgreSQL
2. Verifica que el nombre de la base de datos sea correcto
3. Asegúrate de que el usuario tenga acceso a la base de datos

### Error: "psycopg2 not found"
1. Instala psycopg2: `pip install psycopg2-binary`
2. Si hay problemas, usa: `pip install psycopg2`
3. En Windows, considera usar conda: `conda install psycopg2`

### Error: "PostgreSQL syntax error"
1. Verifica que estés usando la sintaxis correcta de PostgreSQL
2. Las queries incluyen `ORDER BY` automáticamente
3. Si persiste, verifica que estés usando la versión actualizada

### Error: "Puerto en uso"
```bash
# Cambiar puerto en .env
PORT=8001

# O liberar el puerto 8000
netstat -ano | findstr :8000
taskkill /PID XXXX /F
```

### Error: "Not an executable object: 'SELECT 1'"
1. Este error ya está solucionado
2. La función `test_connection` usa `text("SELECT 1")` correctamente

## Testing

### Con Swagger UI
1. Ejecuta la API
2. Abre `http://localhost:8000/docs`
3. Usa la interfaz interactiva para probar endpoints

### Con Postman
1. Importa la colección de ejemplo
2. Configura las variables de entorno
3. Ejecuta las requests de prueba

### Con curl
```bash
# Health check
curl http://localhost:8000/health

# Obtener usuarios (requiere rol admin)
curl http://localhost:8000/users

# Crear usuario admin
curl -X POST "http://localhost:8000/users" \
     -H "Content-Type: application/json" \
     -d '{"username":"test","email":"test@test.com","password":"test123","rol":"admin"}'

# Obtener materiales (acceso público)
curl http://localhost:8000/materials

# Obtener solo libros
curl "http://localhost:8000/materials?type=book"
```

## Despliegue en Producción

### Variables de Entorno de Producción
```env
# Configuración de producción
DATABASE_URL=postgresql://usuario:contraseña@servidor-produccion:5432/sistema_biblioteca
HOST=0.0.0.0
PORT=8000
WORKERS=4
DEBUG=false
RELOAD=false
```

### Comando de Producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

## Recursos Adicionales

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Guía de psycopg2](https://www.psycopg.org/docs/)
- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)

## Autores del Proyecto

### José Manuel Bernal Yepes
- **GitHub**: [JBernal27](https://github.com/JBernal27)
- **LinkedIn**: [Jose Manuel Bernal Yepes](https://www.linkedin.com/in/jose-manuel-bernal-yepes)
- **Email**: jomabeye@gmail.com

### Emmanuel Cardona Alvarez
- **GitHub**: [Emmael2005](https://github.com/Emmael2005)
- **LinkedIn**: [Emmanuel Cardona Alvarez](https://www.linkedin.com/in/emmanuel-cardona-alvarez)
- **Email**: emmaca1995@gmail.com

---

**Proyecto desarrollado para:** Parcial 1 - Aplicaciones y Servicios Web  
**Herramientas utilizadas:** FastAPI, Uvicorn, Postman, GitHub, SQLAlchemy y PostgreSQL

