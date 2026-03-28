"""Domain-level exceptions for Alke Wallet."""


class AlkeWalletError(Exception):
    """Base exception for all domain errors."""


class InsufficientFundsError(AlkeWalletError):
    """Raised when a withdrawal exceeds the available balance."""

    def __init__(self, balance: float, amount: float) -> None:
        self.balance = balance
        self.amount = amount
        super().__init__(
            f"Saldo insuficiente. Disponible: {balance}, solicitado: {amount}."
        )


class InvalidAmountError(AlkeWalletError):
    """Raised when a transaction amount is zero or negative."""

    def __init__(self, amount: float) -> None:
        self.amount = amount
        super().__init__(f"El monto debe ser mayor a cero. Recibido: {amount}.")


class AccountNotFoundError(AlkeWalletError):
    """Raised when no account is found for the requested user."""
