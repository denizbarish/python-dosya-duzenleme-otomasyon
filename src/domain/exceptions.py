class DomainError(Exception):
    """Domain katmanındaki tüm özel hataların taban sınıfı."""


class InvalidPathError(DomainError):
    """Geçersiz veya bulunamayan yol hatası."""


class InvalidOperationError(DomainError):
    """İzin verilmeyen işlem hatası."""
