# 📄 Documento Explicativo — Modelo de Datos y Operaciones CRUD
## Proyecto: Alke Wallet Web — Módulo 7

---

## 1. Modelos Creados

### 1.1 `User` (`apps/users/models.py`)

Representa a un usuario registrado en la plataforma.

```python
class User(models.Model):
    name       = models.CharField(max_length=150)
    email      = models.EmailField(unique=True)
    password   = models.CharField(max_length=255)   # hash PBKDF2-SHA256
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Restricciones relevantes:**
- `email` es único a nivel de base de datos (`unique=True`) y validado con `EmailValidator`.
- `password` almacena siempre el hash, nunca la contraseña en texto plano.
- `is_active` permite deshabilitar usuarios sin eliminarlos (soft disable).

---

### 1.2 `Account` (`apps/accounts/models.py`)

Representa la cuenta financiera asociada a un usuario.

```python
class Account(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    balance    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Restricciones relevantes:**
- `OneToOneField` garantiza que un usuario tenga exactamente una cuenta.
- `on_delete=CASCADE`: al eliminar un usuario, su cuenta se elimina automáticamente.
- `balance` usa `DecimalField` para evitar errores de precisión flotante en montos financieros.

---

### 1.3 `Transaction` (`apps/transactions/models.py`)

Registra cada movimiento financiero (depósito o retiro) sobre una cuenta.

```python
class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT  = "DEPOSIT",  "Depósito"
        WITHDRAW = "WITHDRAW", "Retiro"

    account          = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount           = models.DecimalField(max_digits=14, decimal_places=2,
                                           validators=[validate_positive_amount])
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    description      = models.CharField(max_length=255, blank=True, default="")
    created_at       = models.DateTimeField(auto_now_add=True)
```

**Restricciones relevantes:**
- `ForeignKey` con `on_delete=CASCADE`: al eliminar una cuenta, todas sus transacciones se eliminan.
- `amount` está validado con `validate_positive_amount` (debe ser `> 0`).
- `transaction_type` usa `TextChoices` para garantizar valores controlados.

---

## 2. Relaciones entre Modelos

```
User ──(OneToOne)──► Account ──(ForeignKey)──► Transaction
         1                1                          N
```

| Relación              | Tipo         | `on_delete` | Descripción                                     |
|-----------------------|--------------|-------------|-------------------------------------------------|
| User → Account        | OneToOneField| CASCADE     | 1 usuario = 1 cuenta; eliminar usuario borra cuenta |
| Account → Transaction | ForeignKey   | CASCADE     | 1 cuenta = N transacciones; eliminar cuenta borra transacciones |

---

## 3. Operaciones CRUD Implementadas

Todas las operaciones se realizan desde el navegador siguiendo el flujo:

```
Template → View → Service → ORM → Base de Datos (SQLite)
```

### 3.1 Usuarios

| Operación | Vista           | Servicio            | ORM Utilizado              |
|-----------|----------------|---------------------|----------------------------|
| Crear     | `user_create`  | `create_user()`     | `User(...).save()`         |
| Leer      | `user_list`    | —                   | `User.objects.all()`       |
| Detalle   | `user_detail`  | —                   | `User.objects.get(pk=pk)`  |
| Editar    | `user_update`  | `update_user()`     | `user.save(update_fields=…)`|
| Eliminar  | `user_delete`  | `delete_user()`     | `user.delete()`            |

### 3.2 Cuentas

| Operación | Vista             | Servicio             | ORM Utilizado                      |
|-----------|------------------|----------------------|------------------------------------|
| Crear     | `account_create` | `create_account()`   | `Account(...).save()`              |
| Leer      | `account_list`   | —                    | `Account.objects.select_related()` |
| Detalle   | `account_detail` | —                    | `Account.objects.get(pk=pk)`       |
| Editar    | `account_update` | —                    | `form.save()`                      |
| Eliminar  | `account_delete` | `delete_account()`   | `account.delete()`                 |

### 3.3 Transacciones

| Operación | Vista                   | Servicio             | ORM Utilizado                      |
|-----------|------------------------|----------------------|------------------------------------|
| Crear     | `transaction_create`   | `deposit()` / `withdraw()` | `Transaction.objects.create()` + `Account.objects.filter().update()` (atomic) |
| Leer      | `transaction_list`     | —                    | `Transaction.objects.select_related()` |
| Detalle   | `transaction_detail`   | —                    | `Transaction.objects.get(pk=pk)`   |
| Eliminar  | `transaction_delete`   | `delete_transaction()`| `tx.delete()`                     |

> Las transacciones no tienen edición por diseño: los movimientos financieros son inmutables.

---

## 4. Checklist de Verificación Final

- [x] El proyecto se ejecuta sin errores con `python manage.py runserver`
- [x] Los modelos tienen campos, tipos y restricciones correctas
- [x] Los modelos tienen relaciones con `on_delete` definido
- [x] Las migraciones se generan y aplican sin errores
- [x] Se puede CREAR un usuario, cuenta y transacción desde el navegador
- [x] Se puede VER la lista de usuarios, cuentas y transacciones
- [x] Se puede ver el DETALLE de cada registro
- [x] Se puede EDITAR un usuario y una cuenta
- [x] Se puede ELIMINAR cualquier registro con confirmación previa
- [x] Los datos persisten en `db.sqlite3` después de cada operación
- [x] 31 tests pasan correctamente (`python manage.py test apps`)
