# 🏦 Alke Wallet Web

Aplicación web de gestión de usuarios y transacciones financieras básicas para la empresa FinTech ficticia **Alke Financial**, desarrollada con **Django 5 + SQLite**.

> Proyecto académico — Módulo 7: Acceso a Datos con Django  
> Repositorio: <https://github.com/RobertoOtarola/alke_wallet_web>

---

## 📑 Índice

1. [Modelo de Datos](#1-modelo-de-datos)
2. [Arquitectura](#2-arquitectura)
3. [Estructura del Proyecto](#3-estructura-del-proyecto)
4. [Requisitos Previos](#4-requisitos-previos)
5. [Instalación y Configuración](#5-instalación-y-configuración)
6. [Operaciones CRUD](#6-operaciones-crud)
7. [Flujo de Negocio — Transacciones](#7-flujo-de-negocio--transacciones)
8. [Tests](#8-tests)
9. [Backlog Scrumban](#9-backlog-scrumban)
10. [Errores Frecuentes y Soluciones](#10-errores-frecuentes-y-soluciones)
11. [Roadmap Futuro](#11-roadmap-futuro)

---

## 1. Modelo de Datos

### Diagrama Entidad–Relación

```
┌──────────────┐        ┌──────────────────┐        ┌───────────────────────┐
│     User     │        │     Account      │        │      Transaction      │
├──────────────┤        ├──────────────────┤        ├───────────────────────┤
│ id (PK)      │1      1│ id (PK)          │1      N│ id (PK)               │
│ name         │───────▶│ user (FK→User)   │◀───────│ account (FK→Account)  │
│ email unique │        │ balance Decimal  │        │ amount Decimal        │
│ password     │        │ is_active Bool   │        │ transaction_type Enum │
│ is_active    │        │ created_at       │        │   DEPOSIT | WITHDRAW  │
│ created_at   │        │ updated_at       │        │ description           │
└──────────────┘        └──────────────────┘        │ created_at            │
                                                    └───────────────────────┘
```

### Descripción de los modelos

#### `User` — `apps/users/models.py`

| Campo        | Tipo           | Restricciones                        |
|-------------|----------------|--------------------------------------|
| `id`        | BigAutoField   | PK, autoincremental                  |
| `name`      | CharField(150)  | Requerido                            |
| `email`     | EmailField     | Único, validación de formato         |
| `password`  | CharField(255)  | Hash PBKDF2-SHA256, nunca texto plano|
| `is_active` | BooleanField   | Default `True`                       |
| `created_at`| DateTimeField  | Auto, `auto_now_add=True`            |

#### `Account` — `apps/accounts/models.py`

| Campo        | Tipo                | Restricciones                                |
|-------------|---------------------|----------------------------------------------|
| `id`        | BigAutoField        | PK, autoincremental                          |
| `user`      | OneToOneField(User) | `on_delete=CASCADE`; un usuario = una cuenta |
| `balance`   | DecimalField(14,2)  | Default `0`                                  |
| `is_active` | BooleanField        | Default `True`                               |
| `created_at`| DateTimeField       | Auto, `auto_now_add=True`                    |
| `updated_at`| DateTimeField       | Auto, `auto_now=True`                        |

#### `Transaction` — `apps/transactions/models.py`

| Campo              | Tipo               | Restricciones                          |
|-------------------|--------------------|----------------------------------------|
| `id`              | BigAutoField       | PK, autoincremental                    |
| `account`         | ForeignKey(Account)| `on_delete=CASCADE`; N transacciones   |
| `amount`          | DecimalField(14,2) | Validator `> 0`                        |
| `transaction_type`| CharField(10)      | Enum: `DEPOSIT` \| `WITHDRAW`          |
| `description`     | CharField(255)     | Opcional (`blank=True`)                |
| `created_at`      | DateTimeField      | Auto, `auto_now_add=True`              |

### Relaciones

- **User → Account**: `OneToOne`. Un usuario tiene exactamente una cuenta. Al eliminar un usuario, su cuenta se elimina en cascada (`CASCADE`).
- **Account → Transaction**: `ForeignKey`. Una cuenta puede tener múltiples transacciones. Al eliminar una cuenta, sus transacciones se eliminan en cascada (`CASCADE`).

---

## 2. Arquitectura

El proyecto sigue el patrón **MTV de Django** con una **Services Layer** explícita para aislar la lógica de negocio de las vistas.

```
Presentation Layer   →   Templates (.html) + Views (views.py)
Application Layer    →   Services (services.py)
Domain Layer         →   Models (models.py) + Exceptions + Validators
Infrastructure Layer →   SQLite (db.sqlite3) + Django ORM
```

**Principios aplicados:**

- **Fat Models, Thin Views**: la lógica reside en los modelos y servicios, no en las vistas.
- **Services Layer obligatoria**: ninguna vista escribe directamente en la base de datos; delega en `services.py`.
- **Separation of Concerns**: cada app (users, accounts, transactions) es independiente y desacoplada.
- **Atomicidad**: las operaciones financieras usan `django.db.transaction.atomic()` para garantizar consistencia.

---

## 3. Estructura del Proyecto

```
alke_wallet_web/
│
├── config/                         # Configuración global Django
│   ├── settings/
│   │   ├── base.py                 # Settings compartidos
│   │   ├── dev.py                  # Desarrollo (DEBUG=True)
│   │   └── prod.py                 # Producción
│   ├── urls.py                     # Router raíz
│   └── wsgi.py
│
├── apps/
│   ├── users/                      # EPIC 2: Gestión de Usuarios
│   │   ├── migrations/
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_services.py
│   │   │   └── test_views.py
│   │   ├── models.py               # Modelo User
│   │   ├── forms.py                # UserForm / UserUpdateForm
│   │   ├── services.py             # create/update/delete_user
│   │   ├── views.py                # CRUD views
│   │   └── urls.py
│   │
│   ├── accounts/                   # EPIC 3: Gestión de Cuentas
│   │   ├── migrations/
│   │   ├── tests/
│   │   │   └── test_services.py
│   │   ├── models.py               # Modelo Account
│   │   ├── forms.py
│   │   ├── services.py             # create/delete_account
│   │   ├── views.py
│   │   └── urls.py
│   │
│   └── transactions/               # EPIC 4: Transacciones
│       ├── migrations/
│       ├── tests/
│       │   └── test_services.py
│       ├── models.py               # Modelo Transaction
│       ├── forms.py
│       ├── services.py             # deposit / withdraw (atomic)
│       ├── views.py
│       └── urls.py
│
├── core/                           # Utilidades compartidas
│   ├── exceptions.py               # InsufficientFundsError, etc.
│   └── validators.py               # validate_positive_amount
│
├── templates/                      # Templates globales
│   ├── base.html                   # Layout maestro Bootstrap 5
│   ├── users/
│   ├── accounts/
│   └── transactions/
│
├── static/
│   └── css/main.css
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 4. Requisitos Previos

| Herramienta | Versión mínima |
|------------|---------------|
| Python     | 3.10          |
| pip        | 23.x          |
| Git        | 2.x           |

---

## 5. Instalación y Configuración

### Clonar el repositorio

```bash
git clone https://github.com/RobertoOtarola/alke_wallet_web.git
cd alke_wallet_web
```

### Crear y activar el entorno virtual

```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Generar y aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

Los archivos de migración se generan automáticamente en `apps/<app>/migrations/`.  
El archivo `db.sqlite3` se crea en la raíz del proyecto — **incluirlo en la entrega**.

### (Opcional) Crear superusuario para el Admin de Django

```bash
python manage.py createsuperuser
```

### Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación queda disponible en **<http://127.0.0.1:8000>**.

---

## 6. Operaciones CRUD

Las cuatro operaciones fundamentales están implementadas **desde la interfaz web** (Template → Vista → Servicio → ORM → Base de datos).

### Usuarios (`/users/`)

| Operación | URL                       | Método HTTP | Descripción                          |
|-----------|---------------------------|-------------|--------------------------------------|
| Listar    | `/users/`                 | GET         | Tabla con todos los usuarios         |
| Crear     | `/users/create/`          | GET + POST  | Formulario de registro               |
| Detalle   | `/users/<pk>/`            | GET         | Datos del usuario + cuenta asociada  |
| Editar    | `/users/<pk>/edit/`       | GET + POST  | Actualizar nombre, email, estado     |
| Eliminar  | `/users/<pk>/delete/`     | GET + POST  | Confirmación antes de eliminar       |

### Cuentas (`/accounts/`)

| Operación | URL                         | Método HTTP | Descripción                            |
|-----------|-----------------------------|-------------|----------------------------------------|
| Listar    | `/accounts/`                | GET         | Tabla de cuentas con saldos            |
| Crear     | `/accounts/create/`         | GET + POST  | Asociar cuenta a un usuario existente  |
| Detalle   | `/accounts/<pk>/`           | GET         | Saldo + historial de transacciones     |
| Editar    | `/accounts/<pk>/edit/`      | GET + POST  | Activar / desactivar cuenta            |
| Eliminar  | `/accounts/<pk>/delete/`    | GET + POST  | Confirmación antes de eliminar         |

### Transacciones (`/transactions/`)

| Operación | URL                                      | Método HTTP | Descripción                        |
|-----------|------------------------------------------|-------------|------------------------------------|
| Listar    | `/transactions/`                         | GET         | Historial global de transacciones  |
| Crear     | `/transactions/create/<account_pk>/`     | GET + POST  | Depósito o retiro sobre una cuenta |
| Detalle   | `/transactions/<pk>/`                    | GET         | Detalle de una transacción         |
| Eliminar  | `/transactions/<pk>/delete/`             | GET + POST  | Confirmación antes de eliminar     |

> **Nota:** La transacción no tiene formulario de edición intencional. Las operaciones financieras son inmutables por diseño; sólo se pueden eliminar registros (sin reversión automática del saldo) en entornos de desarrollo.

---

## 7. Flujo de Negocio — Transacciones

Toda mutación de saldo pasa por `apps/transactions/services.py` y es atómica.

### Depósito

```
1. Validar monto > 0           → InvalidAmountError si falla
2. Crear registro Transaction  → tipo DEPOSIT
3. Actualizar Account.balance  → balance + monto
   (todo dentro de atomic())
```

### Retiro

```
1. Validar monto > 0           → InvalidAmountError si falla
2. Bloquear fila con select_for_update()
3. Validar saldo suficiente    → InsufficientFundsError si falla
4. Crear registro Transaction  → tipo WITHDRAW
5. Actualizar Account.balance  → balance - monto
   (todo dentro de atomic())
```

---

## 8. Tests

El proyecto incluye **31 tests** distribuidos en tres categorías:

| Categoría           | Archivo                                       | Tests |
|--------------------|-----------------------------------------------|-------|
| Modelos (Unit)      | `apps/users/tests/test_models.py`             | 4     |
| Servicios (Unit)    | `apps/users/tests/test_services.py`           | 5     |
| Servicios (Unit)    | `apps/accounts/tests/test_services.py`        | 4     |
| Servicios (Unit)    | `apps/transactions/tests/test_services.py`    | 9     |
| Vistas (Integration)| `apps/users/tests/test_views.py`              | 9     |

### Ejecutar los tests

```bash
# Todos los tests
python manage.py test apps --verbosity=2

# Solo una app
python manage.py test apps.transactions --verbosity=2
```

Resultado esperado: `Ran 31 tests … OK`

---

## 9. Backlog Scrumban

La metodología **Scrumban** combina la gestión continua de backlog de Kanban con iteraciones cortas de Scrum.

| WIP Limit | Columnas del tablero                               |
|----------|----------------------------------------------------|
| 3 tareas | `Backlog → Ready → In Progress → Review → Done`    |

### Epics completadas

| Epic | Objetivo                     | Estado |
|------|------------------------------|--------|
| 1    | Setup del proyecto           | ✅ Done |
| 2    | Gestión de Usuarios (CRUD)   | ✅ Done |
| 3    | Gestión de Cuentas (CRUD)    | ✅ Done |
| 4    | Transacciones financieras    | ✅ Done |
| 5    | UI básica (Bootstrap 5)      | ✅ Done |
| 6    | Testing (31 tests)           | ✅ Done |
| 7    | DevOps básico (Git, README)  | ✅ Done |

---

## 10. Errores Frecuentes y Soluciones

| Error                                             | Causa                              | Solución                                      |
|---------------------------------------------------|------------------------------------|-----------------------------------------------|
| `No module named 'crispy_forms'`                  | Dependencias no instaladas         | `pip install -r requirements.txt`             |
| `OperationalError: no such table`                 | Migraciones no aplicadas           | `python manage.py migrate`                    |
| `IntegrityError: UNIQUE constraint failed: email` | Email duplicado                    | Usar un email diferente                       |
| `InsufficientFundsError`                          | Retiro mayor al saldo              | Verificar saldo antes de retirar              |
| `TemplateDoesNotExist`                            | `DIRS` mal configurado en settings | Verificar `BASE_DIR / "templates"` en base.py |
| `django.core.exceptions.ImproperlyConfigured`     | `app_name` faltante en urls.py     | Agregar `app_name = "..."` en cada urls.py    |

---

## 11. Roadmap Futuro

- [ ] Migración a **PostgreSQL**
- [ ] **API REST** con Django REST Framework + JWT
- [ ] Autenticación real con `AbstractUser` de Django
- [ ] Contenedores con **Docker** + `docker-compose`
- [ ] **CI/CD** con GitHub Actions
- [ ] Cobertura de tests ≥ 80 % con `coverage.py`

---

## Información del proyecto

| Atributo    | Valor                                                    |
|------------|----------------------------------------------------------|
| Framework  | Django 5.0.6                                             |
| Base de datos | SQLite (development) / PostgreSQL (producción futura) |
| Frontend   | Bootstrap 5.3 + Bootstrap Icons                          |
| Metodología| Scrumban                                                 |
| Control de versiones | Git — GitHub                                  |
| Autor      | Roberto Otarola                                          |
