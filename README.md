# 🏦 Alke Wallet Web

Aplicación web de gestión de usuarios y transacciones financieras para la empresa FinTech ficticia **Alke Financial**, desarrollada con **Django 5, PostgreSQL y Docker**.

> Proyecto académico — Módulo 7: Acceso a Datos con Django  
> Repositorio: <https://github.com/RobertoOtarola/alke_wallet_web>

---

## 📑 Índice

1. [Modelo de Datos](#1-modelo-de-datos)
2. [Arquitectura y Seguridad (RBAC)](#2-arquitectura-y-seguridad-rbac)
3. [Estructura del Proyecto](#3-estructura-del-proyecto)
4. [Requisitos Previos](#4-requisitos-previos)
5. [Instalación con Docker (Recomendado)](#5-instalación-con-docker-recomendado)
6. [Instalación Local (Desarrollo)](#6-instalación-local-desarrollo)
7. [Operaciones CRUD y Roles](#7-operaciones-crud-y-roles)
8. [Flujo de Negocio — Transacciones](#8-flujo-de-negocio--transacciones)
9. [Tests](#9-tests)
10. [Roadmap](#10-roadmap)

---

## 1. Modelo de Datos

El sistema hereda del sistema de autenticación primario de Django usando `AbstractUser`, garantizando un standard de seguridad robusto con contraseñas encriptadas.

### Diagrama Entidad–Relación

```text
┌───────────────────────┐        ┌──────────────────┐        ┌───────────────────────┐
│ User (AbstractUser)   │        │     Account      │        │      Transaction      │
├───────────────────────┤        ├──────────────────┤        ├───────────────────────┤
│ id (PK)               │1      1│ id (PK)          │1      N│ id (PK)               │
│ name                  │───────▶│ user (FK→User)   │◀───────│ account (FK→Account)  │
│ email (USERNAME_FIELD)│        │ balance Decimal  │        │ amount Decimal        │
│ password (Hashed)     │        │ is_active Bool   │        │ transaction_type Enum │
│ is_staff              │        │ created_at       │        │   DEPOSIT | WITHDRAW  │
│ is_active             │        │ updated_at       │        │ description           │
└───────────────────────┘        └──────────────────┘        │ created_at            │
                                                             └───────────────────────┘
```

---

## 2. Arquitectura y Seguridad (RBAC)

El proyecto sigue el patrón **MTV de Django** potenciado por vistas basadas en clases (**CBVs**), y una **Services Layer** para resguardar la lógica de negocio usando **Atomic Transactions**.

### Control de Acceso Basado en Roles (RBAC)
- **Cliente:** Puede registrarse públicamente (creando automáticamente su cuenta banacaria con saldo cero). Solamente tiene acceso a visualizar e interactuar con su propia información y balances. El cliente es el único con la facultad operativa de crear o alterar saldos sobre su billetera.
- **Staff / Admin:** Posee facultades para listar de manera global a todos los clientes, sus saldos y sus movimientos en el banco; sin embargo **no** puede crear transacciones financieras operativas para no alterar las cuentas (solo el SuperAdmin o el Cliente dueño).

---

## 3. Estructura del Proyecto

```text
alke_wallet_web/
│
├── config/                         # Configuración core de Django
│   ├── settings/
│   │   ├── base.py                 # Settings compartidos + Django REST Framework
│   │   ├── dev.py                  # Desarrollo SQLite local
│   │   └── prod.py                 # Entorno productivo PostgreSQL + Env Vars
│   └── urls.py                     # Router maestro
│
├── apps/
│   ├── users/                      # Modelo Custom User (AbstractUser) y Autenticación
│   ├── accounts/                   # Dominio de Billeteras Virtuales
│   └── transactions/               # Motor de Transferencias y Atomicidad
│
├── core/                           # Excepciones financieras (InsufficientFundsError)
├── templates/                      # Interfaces (Bootstrap 5, Crispy Forms, Humanize)
├── Dockerfile                      # Imagen para contenedor ligero Python (3.12-slim)
├── docker-compose.yml              # Clúster Multi-contenedor (Web + Postgres 16)
└── requirements.txt                # Dependencias (Django, DRF, Psycopg2)
```

---

## 4. Requisitos Previos

| Herramienta | Versión recomendada |
|------------|---------------------|
| Docker     | 24.x+               |
| Python     | 3.12+               |

---

## 5. Instalación con Docker (Recomendado)

El empaquetado utiliza `python:3.12-slim` y delega la base de datos a `postgres:16-alpine`.

1. Clona el repositorio y entra al directorio:
```bash
git clone https://github.com/RobertoOtarola/alke_wallet_web.git
cd alke_wallet_web
```

2. Levanta la arquitectura completa (en background):
```bash
docker-compose up -d --build
```

3. Ejecuta migraciones y crea el primer SuperUsuario:
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

4. Visita: **<http://localhost:8000>**

---

## 6. Instalación Local (Desarrollo estándar sin Docker)

1. Crea y activa tu entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instala dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta migraciones y el servidor en Sqlite (`dev.py`):
```bash
python manage.py migrate
python manage.py runserver
```

---

## 7. Operaciones CRUD y Roles

La plataforma delega de forma asertiva lo que cada rol puede transaccionar. Modulos implementados bajo **CBVs** (Class-Based Views) y mixins de acceso:

### Usuarios y Autenticación
- **`/login/`**: Permite ingreso controlado en Bootstrap 5.
- **`/users/create/`**: Abierto para Auto-Registro de clientes nuevos. Instancia globalmente una `Account` atómica de bienvenida.
- **`/users/`**: Área restringida solo para perfil `Staff`. Central de información de todos los clientes registrados.

### Cuentas (`/accounts/`)
- Muestra los fondos formateados geográficamente y sin decimales (`floatformat:0`). El listado se encuentra oculto para clientes (solo cuenta particular a través de **"Mi Cuenta"**). Redirecciones `HTTP 403 Forbidden` cuidan la manipulación de URLs de otras cuentas ajenas.

### Transacciones (`/transactions/`)
- Interfaz bloqueada para `Staff`. Protecciones in-view para saldos insuficientes o nulos que se emiten al UI bajo estandartes `alert-danger` de error visuales.

---

## 8. Flujo de Negocio — Transacciones

Toda mutación de saldo pasa por la Service Layer.

### Depósito / Retiro Atómico
```text
1. Validar montos lógicos (>0)
2. Bloquear fila con select_for_update() (seguridad estructural ante concurrencia)
3. Balance check (Solo para retiros)
4. Update balance (DB Update)
5. Create transaction Record
   (TODO garantizado y envuelto bajo proceso django.db.transaction.atomic)
```

---

## 9. Tests

La suite principal cuenta con **35 tests Integrales** simulando concurrencias e interdependencia bajo accesos emulados:

```bash
# Ejecutar toda la suite
python manage.py test apps --verbosity=2
```
✅ **Resultado**: `Ran 35 tests ... OK`

---

## 10. Roadmap

- [x] Autenticación real nativa con `AbstractUser` de Django
- [x] Autenticación/Perfiles: Roles (RBAC) usando `Class-Based Views`
- [x] Migración backend: Settings adaptables condicionados para base de datos **PostgreSQL**
- [x] Contenedores optimizados con **Docker** + `docker-compose`
- [ ] Incorporar App **API REST** de endpoints (`Django REST Framework`)
- [ ] Documentación Swagger / OpenAPI para infraestructura
- [ ] Cobertura de tests ≥ 90 %

---

## 11. Licencia

GPL-3.0
