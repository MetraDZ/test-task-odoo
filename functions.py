from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from db import Session, User
from classes import UserDB, UserRegistration, TokenData
from constants import MINIMUM_PASSWORD_LENGTH, MINIMUM_USERNAME_LENGTH, SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    with Session.begin() as session:
        user = session.query(User).where(User.username==username).scalar()
        if user:
            return UserDB(**user.__dict__)
    
def check_and_extract_data(user_data: UserRegistration):
    if get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username already exists",
        )
    if len(user_data.username) < MINIMUM_USERNAME_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username must be at least {MINIMUM_USERNAME_LENGTH} characters long",
        )
    if user_data.username[0].isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username can't start with digit",
        )
    if len(user_data.password) < MINIMUM_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password must be at least {MINIMUM_PASSWORD_LENGTH} characters long",
        )
    return user_data.model_dump()

def add_user_to_db(user_data: dict):
    with Session.begin() as session:
        new_user = User(
            username=user_data["username"],
            hashed_password = get_password_hash(user_data['password']),
        )
        session.add(new_user)
        session.commit()

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    '''
    Receives and decodes JWT token:
        key `sub` (subject): user's username, who token belongs to
    Wrong JWT token will cause exception.
    Returns authenticated user, if JWT token is valid.
    '''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if not username:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if not user:
        raise credentials_exception
    return user