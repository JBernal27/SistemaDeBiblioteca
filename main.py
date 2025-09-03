from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import create_tables, test_connection, migrate_database
from endpoints import get_users_router, post_user_router, put_user_router, delete_user_router, get_materials_router, post_material_router, put_material_router, delete_material_router

# Crear la aplicación FastAPI
app = FastAPI(
    title="Sistema de Biblioteca API",
    description="Desarrollo de una API REST completa para un sistema de biblioteca donde puedes gestionar libros, revistas y periódicos.",
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
app.include_router(get_materials_router)
app.include_router(post_material_router)
app.include_router(put_material_router)
app.include_router(delete_material_router)

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    try:
        if test_connection():
            create_tables()
            migrate_database()
            print("API iniciada correctamente")
            print("Base de datos conectada, tablas creadas y migración completada")
        else:
            print("No se pudo conectar a la base de datos")
    except Exception as e:
        print(f"Error al inicializar la API: {e}")

@app.get("/health")
async def health_check():
    """Verificación del estado de la API"""
    db_status = "connected" if test_connection() else "disconnected"
    return {"status": "healthy", "database": db_status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
