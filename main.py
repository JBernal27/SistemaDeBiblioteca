from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import create_tables, test_connection, migrate_database
from endpoints import (
    get_users_router,
    put_user_router,
    delete_user_router,
    get_materials_router,
    post_material_router,
    put_material_router,
    delete_material_router,
    get_loan_router,
    post_loan_router,
    put_loan_router,
    login_router,
    register_router,
)

"""
Crear la aplicación FastAPI
"""
app = FastAPI(
    title="Sistema de Biblioteca API",
    description="Desarrollo de una API REST completa para un sistema de biblioteca donde puedes gestionar libros, revistas y periódicos.",
    version="1.0.0",
)

"""
Configurar CORS (Cross-Origin Resource Sharing)
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend
        "http://127.0.0.1:3000",
        "http://localhost:8000",  # Backend (FastAPI)
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "accept"],
)

"""
Incluir routers de autenticación
"""
app.include_router(get_users_router)
app.include_router(put_user_router)
app.include_router(delete_user_router)
app.include_router(get_materials_router)
app.include_router(post_material_router)
app.include_router(put_material_router)
app.include_router(delete_material_router)
app.include_router(get_loan_router)
app.include_router(post_loan_router)
app.include_router(put_loan_router)
app.include_router(login_router)
app.include_router(register_router)


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
