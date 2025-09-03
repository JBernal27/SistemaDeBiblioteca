import enum

class MaterialType(str, enum.Enum):
    book = "book"
    newspaper = "newspaper"
    magazine = "magazine"