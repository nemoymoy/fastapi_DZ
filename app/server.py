from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from lifespan import lifespan
from dependency import SessionDependency, TokenDependency
import models
import crud
import auth
from constants import SUCCESS_RESPONSE

from schema import (GetAdvertisementResponse, CreateAdvertisementResponse, CreateAdvertisementRequest,
                    UpdateAdvertisementRequest, UpdateAdvertisementResponse, DeleteAdvertisementResponse,
                    CreateUserResponse,
                    CreateUserRequest, GetUserResponse, UpdateUserRequest, UpdateUserResponse, DeleteUserResponse,
                    SearchAdvertisementResponse, LoginResponse, LoginRequest)

app = FastAPI(
    title="Advertisement API",
    version="0.1.0",
    description="API for advertisements",
    lifespan=lifespan,
)

@app.post(
    path="/api/v1/advertisement",
    response_model=CreateAdvertisementResponse,
    tags=["create advertisements"])
async def create_advertisement(
        advert_request: CreateAdvertisementRequest,
        session: SessionDependency,
        token: TokenDependency):
    adv_dict = advert_request.model_dump(exclude_unset=True)
    adv_orm_obj = models.Advert( **adv_dict, author_id=token.user_id)
    await crud.add_item(session, adv_orm_obj)
    return adv_orm_obj.id_dict

@app.get(
    path="/api/v1/advertisement/{advertisement_id}",
    response_model=GetAdvertisementResponse,
    tags=["get advertisements"])
async def get_advertisement(
        session: SessionDependency,
        advertisement_id: int):
    adv_orm_obj = await crud.get_item_by_id(session, models.Advert, advertisement_id)
    return adv_orm_obj.dict

@app.get(
    path="/api/v1/advertisement",
    response_model=SearchAdvertisementResponse,
    tags=["search advertisements"])
async def search_advertisement(
        session: SessionDependency,
        title: str):
    query = (
        select(models.Advert)
        .where(models.Advert.title.ilike(f"%{title}%"))
        .limit(10000)
        .options(selectinload(models.Advert.author))
    )
    advs = (await session.scalars(query)).unique().all()
    return {"results": [adv.dict for adv in advs]}

@app.patch(
    path="/api/v1/advertisement/{advertisement_id}",
    response_model=UpdateAdvertisementResponse,
    tags=["update advertisements"])
async def update_advertisement(
        advertisement_id: int,
        advertisement_request: UpdateAdvertisementRequest,
        session: SessionDependency,
        token: TokenDependency):
    adv_dict = advertisement_request.model_dump(exclude_unset=True)
    adv_orm_obj = await crud.get_item_by_id(session, models.Advert, advertisement_id)
    if adv_orm_obj.author_id != token.user_id and token.user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough rights")
    for field, value in adv_dict.items():
        setattr(adv_orm_obj, field, value)
    await crud.add_item(session, adv_orm_obj)
    return SUCCESS_RESPONSE

@app.delete(
    path="/api/v1/advertisement/{advertisement_id}",
    response_model=DeleteAdvertisementResponse,
    tags=["delete advertisements"])
async def delete_advertisement(
        advertisement_id: int,
        session: SessionDependency,
        token: TokenDependency):
    adv_orm_obj = await crud.get_item_by_id(session, models.Advert, advertisement_id)
    if adv_orm_obj.author_id != token.user_id and token.user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough rights")
    await crud.delete_item(session, adv_orm_obj)
    return SUCCESS_RESPONSE

@app.post(
    path="/api/v1/login",
    response_model=LoginResponse,
    tags=["login"])
async def login(
        login_data: LoginRequest,
        session: SessionDependency):
    query = select(models.User).where(models.User.name == login_data.name)
    user = await session.scalar(query)
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not auth.check_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = models.Token(user_id=user.id)
    await crud.add_item(session, token)
    return token.dict

@app.post(
    path="/api/v1/user",
    response_model=CreateUserResponse,
    tags=["create user"])
async def create_user(
        user_request: CreateUserRequest,
        session: SessionDependency):
    user_data_dict = user_request.model_dump()
    user_data_dict["password"] = auth.hash_password(user_data_dict["password"])
    user = models.User(**user_data_dict)
    await crud.add_item(session, user)
    return user.id_dict

@app.get(
    path="/api/v1/user/{user_id}",
    response_model=GetUserResponse,
    tags=["get user"])
async def get_user(
        session: SessionDependency,
        user_id: int):
    user_orm_obj = await crud.get_item_by_id(session, models.User, user_id)
    return user_orm_obj.dict

@app.patch(
    path="/api/v1/user/{user_id}",
    response_model=UpdateUserResponse,
    tags=["update user"])
async def update_user(
        user_id: int,
        user_request: UpdateUserRequest,
        session: SessionDependency,
        token: TokenDependency):
    user_orm_obj = await crud.get_item_by_id(session, models.User, user_id)
    if user_orm_obj.id != token.user_id and token.user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough rights")
    user_dict = user_request.model_dump(exclude_unset=True)
    user_dict["password"] = auth.hash_password(user_dict["password"])
    for field, value in user_dict.items():
        setattr(user_orm_obj, field, value)
    await crud.add_item(session, user_orm_obj)
    return SUCCESS_RESPONSE

@app.delete(
    path="/api/v1/user/{user_id}",
    response_model=DeleteUserResponse,
    tags=["delete user"])
async def delete_user(
        user_id: int,
        session: SessionDependency,
        token: TokenDependency):
    user_orm_obj = await crud.get_item_by_id(session, models.User, user_id)
    if user_orm_obj.id != token.user_id and token.user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough rights")
    await crud.delete_item(session, user_orm_obj)
    return SUCCESS_RESPONSE
