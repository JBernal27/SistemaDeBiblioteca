from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import create_tables, test_connection, migrate_database
from endpoints import get_users_router, post_user_router, put_user_router, delete_user_router

# Crear la aplicación FastAPI
app = FastAPI(
    title="Mi API con SQL Server y SQLAlchemy",
    description="API completa con los 4 métodos HTTP, SQLAlchemy y conexión a SQL Server",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers de los endpoints
app.include_router(get_users_router)
app.include_router(post_user_router)
app.include_router(put_user_router)
app.include_router(delete_user_router)

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    try:
        # Verificar conexión
        if test_connection():
            # Crear las tablas si no existen
            create_tables()
            # Migrar la base de datos
            migrate_database()
            print("API iniciada correctamente")
            print("Base de datos conectada, tablas creadas y migración completada")
        else:
            print("No se pudo conectar a la base de datos")
    except Exception as e:
        print(f"Error al inicializar la API: {e}")

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Bienvenido a Mi API con SQL Server y SQLAlchemy!",
        "version": "1.0.0",
        "technology": "FastAPI + SQLAlchemy + SQL Server",
        "endpoints": {
            "GET /users": "Obtener lista de usuarios",
            "GET /users/{id}": "Obtener usuario específico",
            "POST /users": "Crear nuevo usuario",
            "PUT /users/{id}": "Actualizar usuario",
            "DELETE /users/{id}": "Eliminar usuario (soft delete)",
            "DELETE /users/{id}/hard": "Eliminar usuario permanentemente"
        },
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Verificación del estado de la API"""
    db_status = "connected" if test_connection() else "disconnected"
    return {"status": "healthy", "database": db_status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
