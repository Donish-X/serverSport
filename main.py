from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List, Optional, Union, Dict
from datetime import date
from pydantic import BaseModel
import logging

app = FastAPI()

# Настройка CORS (для разрешения запросов с фронтенда)
origins = ["*"]  # Установите нужные оригины для вашего фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(filename="fastapi.log", level=logging.DEBUG) 

# Настройка базы данных
DATABASE_URL = "postgresql://postgres:postgres@192.168.0.110/sportsmens"
engine = create_engine(DATABASE_URL)

metadata = MetaData()

sportsmens = Table(
    "sportsmens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("gruppa", String),
    Column("birth_date", String),
    Column("adress", String),  # Новое поле адреса
    Column("parent_phone_number", String),  # Новое поле номера телефона родителя
    Column("parent_fio", String),  # Новое поле ФИО родителя
)

gruppa_table = Table(
    "gruppa",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("gruppa", String, nullable=True),
    Column("coach", String, nullable=True),
)


Base = declarative_base()
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Sportsmen(Base):
    __tablename__ = "sportsmens"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    gruppa = Column(String)
    birth_date = Column(String)
    adress = Column(String)  # Новое поле адреса
    parent_phone_number = Column(String)  # Новое поле номера телефона родителя
    parent_fio = Column(String)  # Новое поле ФИО родителя

   


class Gruppa(Base):
    __tablename__ = "gruppa"
    id = Column(Integer, primary_key=True)
    gruppa = Column(String)
    coach = Column(String)



# Pydantic модели для данных запросов
class SportsmenFilterParams(BaseModel):
    group: str


class SportsmenDetailsParams(BaseModel):
    name: str
    date: date

class GruppaResponseModel(BaseModel):
    gruppa: str


# Роуты FastAPI
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/sportsmens/")
async def read_sportsmens():
    db = SessionLocal()
    sportsmens_list = db.query(Sportsmen).all()
    db.close()
    print(sportsmens_list)
    return sportsmens_list


@app.get("/sportsmen/{sportsmen_id}")
async def read_sportsmen(sportsmen_id: int):
    db = SessionLocal()
    sportsmen = db.query(Sportsmen).filter(Sportsmen.id == sportsmen_id).first()
    db.close()
    if sportsmen is None:
        raise HTTPException(status_code=404, detail="Sportsmen not found")
    return sportsmen


@app.post("/api/sportsmens_by_group/")
async def get_sportsmens_by_group(params: SportsmenFilterParams):
    db = SessionLocal()
    filtered_sportsmens = db.query(Sportsmen).filter(Sportsmen.gruppa == params.group).all()
    db.close()
    return filtered_sportsmens


@app.post("/api/sportsmen_details/")
async def post_sportsmen_details(params: SportsmenDetailsParams):
    db = SessionLocal()
    new_sportsmen = Sportsmen(**params.dict())
    db.add(new_sportsmen)
    db.commit()
    db.refresh(new_sportsmen)
    db.close()
    return new_sportsmen

@app.get("/groups/")
async def read_groups():
    db = SessionLocal()
    groups = db.query(Gruppa.gruppa).all()
    db.close()
    return [{"gruppa": group[0]} for group in groups]
