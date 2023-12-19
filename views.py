from datetime import timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Path, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn

from classes import Token, UserModel
from constants import ACCESS_TOKEN_EXPIRE_MINUTES
from db import Contact, Session
from functions import add_user_to_db, authenticate_user, check_and_extract_data, create_access_token, get_current_user


app = FastAPI()

@app.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register", response_class=Response)
async def register(user_data: Annotated[dict, Depends(check_and_extract_data)]):
    add_user_to_db(user_data)
    return Response('Successful registration', status_code=status.HTTP_201_CREATED)


@app.get('/contacts', response_class=JSONResponse)
def view_contacts(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    per_page: int,
    page: int
):
    responce = []
    if per_page < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='per_page must be at least 50'
        )
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page can't be less then 1"
        )
    with Session.begin() as session:
        contacts = session.query(
            Contact
        ).limit(per_page).offset((page - 1) * per_page).all()
        responce = [contact.to_dict() for contact in contacts]
    return JSONResponse({'contacts': responce}, status_code=status.HTTP_200_OK)

@app.get('/contact/{contact_id}', response_class=JSONResponse)
def view_contacts(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    contact_id: Annotated[int, Path(title='Odoo id of contact')]
):
    with Session.begin() as session:
        contact = session.query(
            Contact
        ).filter(Contact.oodo_id == contact_id).scalar()
        if contact:
            responce = contact.to_dict()
        else:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail='No contact with such odoo id'
            )
    return JSONResponse({'contact': responce}, status_code=status.HTTP_200_OK)


if __name__ == "__main__":
    uvicorn.run("views:app", reload=True, log_level='debug')