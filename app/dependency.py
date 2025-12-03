from models import Session, Token
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends, Header, HTTPException

import uuid
from config import TOKEN_TTL_SEC
from sqlalchemy import select
import datetime

async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]

async def get_token(x_token: Annotated[uuid.UUID, Header()], session: SessionDependency) -> Token:
    token_query = select(Token).where(Token.token == x_token, Token.creation_token >= (datetime.datetime.now() - datetime.timedelta(seconds=TOKEN_TTL_SEC)))
    token = await session.scalar(token_query)
    if token is None:
        raise HTTPException(status_code=401, detail="Token is not found")
    return token

TokenDependency = Annotated[Token, Depends(get_token)]
