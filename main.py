import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

DATABASE_URL = "sqlite:///market.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

goods = sqlalchemy.Table(
    "goods",
    metadata,
    sqlalchemy.Column("goods_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(64)),
    sqlalchemy.Column("description", sqlalchemy.String(1000)),
    sqlalchemy.Column("price", sqlalchemy.Float)
)

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("lastname", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("user_password", sqlalchemy.String(10))
)

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("order_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id")),
    sqlalchemy.Column("goods_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("goods.goods_id")),
    sqlalchemy.Column("order_date", sqlalchemy.String(32)),
    sqlalchemy.Column("status", sqlalchemy.String(32))
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

metadata.create_all(engine)

app = FastAPI()


class GoodsIn(BaseModel):
    name: str = Field(..., max_length=64)
    description: str = Field(None, max_length=1000)
    price: float = Field(..., gt=0, le=100000)


class Goods(BaseModel):
    goods_id: int
    name: str = Field(..., max_length=64)
    description: str = Field(None, max_length=1000)
    price: float = Field(..., gt=0, le=100000)


class UserIn(BaseModel):
    name: str = Field(..., max_length=32)
    lastname: str = Field(..., max_length=32)
    email: str = Field(..., max_length=128)
    user_password: str = Field(..., max_length=8)


class User(BaseModel):
    user_id: int
    name: str = Field(..., max_length=32)
    lastname: str = Field(..., max_length=32)
    email: str = Field(..., max_length=128)
    user_password: str = Field(None, max_length=10)


class OrderIn(BaseModel):
    user_id: int = Field(...)
    goods_id: int = Field(...)
    order_date: str = Field(..., max_length=32)
    status: str = Field(None, max_length=32)


class Order(BaseModel):
    order_id: int
    user_id: int
    goods_id: int
    order_date: str = Field(..., max_length=32)
    status: str = Field(None, max_length=32)


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    return {"message": "started"}

@app.get("/users/", response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)

@app.get("/users/{user_id}", response_model=User)
async def read_one_user(user_id: int):
    query = users.select().where(users.c.user_id == user_id)
    return await database.fetch_one(query)

@app.post("/users/", response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(**user.dict())
    last_id = await database.execute(query)
    return {**user.dict(), "user_id": last_id}

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.user_id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "user_id": user_id}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.user_id == user_id)
    await database.execute(query)
    return {"message": "User deleted"}

@app.get("/goods/", response_model=List[Goods])
async def read_goods():
    query = goods.select()
    return await database.fetch_all(query)

@app.get("/goods/{goods_id}", response_model=Goods)
async def read_one_goods(goods_id: int):
    query = goods.select().where(goods.c.goods_id == goods_id)
    return await database.fetch_one(query)

@app.post("/goods/", response_model=Goods)
async def create_goods(new_goods: GoodsIn):
    query = goods.insert().values(**new_goods.dict())
    last_id = await database.execute(query)
    return {**new_goods.dict(), "goods_id": last_id}

@app.put("/goods/{goods_id}", response_model=Goods)
async def update_goods(goods_id: int, new_goods: GoodsIn):
    query = goods.update().where(goods.c.goods_id == goods_id).values(**new_goods.dict())
    await database.execute(query)
    return {**new_goods.dict(), "goods_id": goods_id}

@app.delete("/goods/{goods_id}")
async def delete_goods(goods_id: int):
    query = goods.delete().where(goods.c.goods_id == goods_id)
    await database.execute(query)
    return {"message": "Goods deleted"}

@app.get("/orders/", response_model=List[Order])
async def read_orders():
    query = orders.select()
    return await database.fetch_all(query)

@app.get("/orders/{order_id}", response_model=Order)
async def read_one_order(order_id: int):
    query = orders.select().where(orders.c.order_id == order_id)
    return await database.fetch_one(query)

@app.post("/orders/", response_model=Order)
async def create_order(order: OrderIn):
    query = orders.insert().values(**order.dict())
    last_id = await database.execute(query)
    return {**order.dict(), "order_id": last_id}

@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, order: OrderIn):
    query = orders.update().where(orders.c.order_id == order_id).values(**order.dict())
    await database.execute(query)
    return {**order.dict(), "order_id": order_id}

@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.order_id == order_id)
    await database.execute(query)
    return {"message": "Order deleted"}

