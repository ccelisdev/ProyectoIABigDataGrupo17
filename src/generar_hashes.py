#Generar hashes de contraseñas para los usuarios de prueba

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print("empleado123   ->", pwd_context.hash("empleado123"))
print("compliance123 ->", pwd_context.hash("compliance123"))
print("admin123      ->", pwd_context.hash("admin123"))
