# Endpoints del Sistema de Biblioteca

## Endpoints de Autenticación

### `/auth`
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar nuevo usuario

## Endpoints de Gestión de Datos Maestros

### `/roles` - Gestión de Roles
- `GET /roles/` - Listar roles (Admin)
- `GET /roles/{role_id}` - Obtener rol específico (Admin)
- `POST /roles/` - Crear nuevo rol (Admin)
- `PUT /roles/{role_id}` - Actualizar rol (Admin)
- `DELETE /roles/{role_id}` - Eliminar rol (Admin)

### `/authors` - Gestión de Autores
- `GET /authors/` - Listar autores (Admin)
- `GET /authors/{author_id}` - Obtener autor específico (Admin)
- `POST /authors/` - Crear nuevo autor (Admin)
- `PUT /authors/{author_id}` - Actualizar autor (Admin)
- `DELETE /authors/{author_id}` - Eliminar autor (Admin)

### `/material-types` - Gestión de Tipos de Material
- `GET /material-types/` - Listar tipos de material (Admin)
- `GET /material-types/{material_type_id}` - Obtener tipo específico (Admin)
- `POST /material-types/` - Crear nuevo tipo (Admin)
- `PUT /material-types/{material_type_id}` - Actualizar tipo (Admin)
- `DELETE /material-types/{material_type_id}` - Eliminar tipo (Admin)

### `/loan-status` - Gestión de Estados de Préstamo
- `GET /loan-status/` - Listar estados de préstamo (Admin)
- `GET /loan-status/{loan_status_id}` - Obtener estado específico (Admin)
- `POST /loan-status/` - Crear nuevo estado (Admin)
- `PUT /loan-status/{loan_status_id}` - Actualizar estado (Admin)
- `DELETE /loan-status/{loan_status_id}` - Eliminar estado (Admin)

## Endpoints Existentes

### `/users` - Gestión de Usuarios
- `GET /users/` - Listar usuarios (Admin)
- `GET /users/{user_id}` - Obtener usuario específico (Admin/Propio)
- `POST /users/` - Crear usuario (Admin)
- `PUT /users/{user_id}` - Actualizar usuario (Admin)
- `DELETE /users/{user_id}` - Eliminar usuario (Admin)

### `/materials` - Gestión de Materiales
- `GET /materials/` - Listar materiales (Cliente/Admin)
- `GET /materials/{material_id}` - Obtener material específico (Cliente/Admin)
- `POST /materials/` - Crear material (Admin)
- `PUT /materials/{material_id}` - Actualizar material (Admin)
- `DELETE /materials/{material_id}` - Eliminar material (Admin)

### `/loans` - Gestión de Préstamos
- `GET /loans/` - Listar préstamos (Admin)
- `GET /loans/{loan_id}` - Obtener préstamo específico (Admin)
- `POST /loans/` - Crear préstamo (Admin)
- `PUT /loans/{loan_id}` - Actualizar préstamo (Admin)
- `GET /loans/my` - Mis préstamos (Cliente)

## Características de Seguridad

### Autenticación
- Todos los endpoints requieren autenticación JWT
- Tokens incluyen información del usuario y rol
- Sistema de roles: `admin` y `cliente`

### Autorización
- **Admin**: Acceso completo a todos los endpoints
- **Cliente**: Acceso limitado a materiales y sus propios préstamos

### Campos de Auditoría
Todos los endpoints incluyen campos de auditoría:
- `created_by`: UUID del usuario que creó el registro
- `updated_by`: UUID del usuario que modificó el registro
- `updated_at`: Timestamp de la última modificación

### Validaciones
- Validación de unicidad en nombres
- Verificación de relaciones antes de eliminar
- Validación de permisos por rol
- Manejo de errores HTTP apropiados

## Estructura de Archivos

```
endpoints/
├── auth/
│   ├── login.py
│   └── register.py
├── users/
│   ├── get_users.py
│   └── put_user.py
├── materials/
│   ├── post_material.py
│   └── put_material.py
├── loans/
│   ├── get_loan.py
│   └── post_loan.py
├── roles/                    # Nuevos endpoints
│   ├── get_roles.py
│   ├── post_role.py
│   ├── put_role.py
│   └── delete_role.py
├── authors/                  # Nuevos endpoints
│   ├── get_authors.py
│   ├── post_author.py
│   ├── put_author.py
│   └── delete_author.py
├── material_types/           # Nuevos endpoints
│   ├── get_material_types.py
│   ├── post_material_type.py
│   ├── put_material_type.py
│   └── delete_material_type.py
└── loan_status/             # Nuevos endpoints
    ├── get_loan_status.py
    ├── post_loan_status.py
    ├── put_loan_status.py
    └── delete_loan_status.py
```
