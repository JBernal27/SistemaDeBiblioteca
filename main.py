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
    get_roles_router,
    post_role_router,
    put_role_router,
    delete_role_router,
    get_authors_router,
    post_author_router,
    put_author_router,
    delete_author_router,
    get_material_types_router,
    post_material_type_router,
    put_material_type_router,
    delete_material_type_router,
    get_loan_status_router,
    post_loan_status_router,
    put_loan_status_router,
    delete_loan_status_router,
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
Incluir routers de la aplicación
"""
# Routers de autenticación
app.include_router(login_router)
app.include_router(register_router)

# Routers de usuarios
app.include_router(get_users_router)
app.include_router(put_user_router)
app.include_router(delete_user_router)

# Routers de materiales
app.include_router(get_materials_router)
app.include_router(post_material_router)
app.include_router(put_material_router)
app.include_router(delete_material_router)

# Routers de préstamos
app.include_router(get_loan_router)
app.include_router(post_loan_router)
app.include_router(put_loan_router)

# Routers de roles
app.include_router(get_roles_router)
app.include_router(post_role_router)
app.include_router(put_role_router)
app.include_router(delete_role_router)

# Routers de autores
app.include_router(get_authors_router)
app.include_router(post_author_router)
app.include_router(put_author_router)
app.include_router(delete_author_router)

# Routers de tipos de material
app.include_router(get_material_types_router)
app.include_router(post_material_type_router)
app.include_router(put_material_type_router)
app.include_router(delete_material_type_router)

# Routers de estados de préstamo
app.include_router(get_loan_status_router)
app.include_router(post_loan_status_router)
app.include_router(put_loan_status_router)
app.include_router(delete_loan_status_router)


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
