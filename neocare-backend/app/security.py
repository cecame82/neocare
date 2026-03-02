from datetime import datetime, timedelta
from typing import Optional
from jose import jwt # Librería para generar el token
from passlib.context import CryptContext # Librería para encriptar passwords
import os
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import database, models

load_dotenv() #Permite acceder a las variables de entorno

# -- CONFIGURACIÓN --
#Leer la clave secreta del .env
SECRET_KEY = os.getenv("SECRET_KEY")
#Asegurarnos primero de que haya clave
if not SECRET_KEY: 
    raise ValueError("No se ha configurado la SECRET_KEY.")
#Definir el algoritmo de encriptación
ALGORITHM = "HS256" #El estándar industrial
#Tiempo de vida del token (min)
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# -- HASHING --
#Uso del esquema "bcrypt", lento pero seguro
#deprecated="auto" -> permite actualizar hashes viejos si cambiamos la seguridad en el futuro
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -- FUNCIONES PASSWORD --

#Verificar: comparar la contraseña plana con el hash guardado en la DB
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#Hash: toma la contraseña plana y devuelve el string encriptado
def get_password_hash(password: str):
    # **CORRECCIÓN:** Truncar la contraseña a 72 caracteres para evitar el límite de bcrypt
    # que causa el ValueError y el error 500.
    truncated_password = password[:72] 
    return pwd_context.hash(truncated_password)

# -- FUNCIONES TOKEN --

#Genera token con los datos del usuario y la fecha de expiración
def create_access_token(data: dict, expires_time: Optional[timedelta] = None):
    to_encode = data.copy() #Copia de los datos para no modificar el original por error
    if expires_time: #Calculamos cuando caduca el token
        expire = datetime.utcnow() + expires_time
    else: #usar el tiempo por defecto sino
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) #añadimos la expiración del diccionario de datos
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#Decodificar el token y obtener los datos
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        # Captura errores específicos de JWT como token expirado o firma inválida
        return None


# -- DEPENDENCIAS DE SEGURIDAD --

# Esquema de autenticación que le dice a FastAPI cómo encontrar el token en el header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Dependencia para obtener el usuario actual a partir de un token.

    1. Recibe el token del esquema OAuth2.
    2. Decodifica el token para obtener el payload.
    3. Extrae el 'subject' (email) del payload.
    4. Busca el usuario en la base de datos.
    5. Si algo falla (token inválido, usuario no encontrado), lanza una excepción HTTP 401.
    
    Returns:
        models.User: El objeto de usuario SQLAlchemy correspondiente.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user