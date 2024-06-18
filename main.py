import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.responses import Response, FileResponse
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import MenuButtonWebApp, WebAppInfo
from aiogram.types.message import ContentType
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.utils import executor as ex
from aiogram.utils.callback_data import CallbackData
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import threading
import sqlite3
import uvicorn

API_TOKEN = '6776253704:AAEoJtMSBzNisMnGG2xhoKvvW3CATlBZtVg'
SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Setup bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


def render_template(path:str):
    file = open(path, "r", encoding="UTF-8")
    return file.read()


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return render_template("main.html")

@app.get("/{file}.{dimention}")
def return_png(file:str, dimention:str):
    file=file+"."+dimention
    return FileResponse(file)

from datetime import datetime

@app.post("/login")
def get_completed_tasks(data = Body()):
    id = data["id"]
    name = data["username"]
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    balance = cursor.execute(f"SELECT balance FROM users WHERE id = '{id}' ORDER BY balance DESC").fetchone()
    if balance == None or balance == (None) or balance == [None]:
        balance = 0
        cursor.execute(f"INSERT INTO users (id, username, balance) VALUES ('{id}', '{name}', '0')")
    conn.commit()
    return JSONResponse({"balance": balance})
    
@app.post("/getLeaderboard")
def get_completed_tasks(data = Body()):
    id = data["id"]
    name = data["username"]
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    data = cursor.execute(f"SELECT username, balance FROM users WHERE id = '{id}' ORDER BY balance DESC").fetchall()
    if data == None or data == (None) or data == [None]:
        cursor.execute(f"INSERT INTO users (id, username, balance) VALUES ('{id}', '{name}', '0')")
        conn.commit()
        data = cursor.execute(f"SELECT username, balance FROM users WHERE id = '{id}' ORDER BY balance DESC").fetchall()
    result = []
    for user in data:
        result.append({"name":user[0], "score":user[1]})
    return JSONResponse({"users": result})
    

    
@app.post("/claimDailyReward")
def get_completed_tasks(data = Body()):
    print(data)
    id = data["id"]
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    date = cursor.execute(f"SELECT time FROM daily WHERE id = '{id}'").fetchone()
    if date == None:
        now = datetime.now()
        date = now.strftime("%d/%m/%Y")
        cursor.execute(f"INSERT INTO daily (id, claimed, time) VALUES ('{id}',true,'{date}')").fetchone()
    else:
        now = datetime.now()
        date = datetime(date.split("/")[2],date.split("/")[1],date.split("/")[0])
        gap = now - date
        days_gap = gap.days
        if days_gap == 1:
            days = int(cursor.execute(f"SELECT days FROM daily WHERE id = '{id}'").fetchone())
            days = days + 1
            cursor.execute(f"UPDATE daily SET days = '{days}', time = '{now.strftime('%d/%m/%Y')}'")
        else:
            cursor.execute(f"UPDATE daily SET days = '1', time = '{now.strftime('%d/%m/%Y')}'")
        
    conn.commit()
    conn.close()
    resp = {"completed": True}
    return JSONResponse(resp)

@app.post("/getDailyCount")
def get_completed_tasks(data = Body()):
    id = data["id"]
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    days = cursor.execute(f"SELECT days FROM daily WHERE id = '{id}'").fetchone()
    if days == None:
        days = 0
    
    conn.commit()
    conn.close()
    resp = {"days": days}
    return JSONResponse(resp)
    
@app.post("/getCompletedTasks")
def get_completed_tasks(data = Body()):
    id = data["id"]
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Создаем таблицу пользователей
    arr = cursor.execute(f"SELECT completed FROM tasks WHERE id = '{id}'").fetchone()
    #arr = id1,id2,id3
    arr = arr.split(",")
    completed_daily = False
    date = cursor.execute(f"SELECT time FROM daily WHERE id = '{id}'").fetchone()
    if date != None:
        now = datetime.now()
        date = datetime(date.split("/")[2],date.split("/")[1],date.split("/")[0])
        gap = now - date
        days_gap = gap.days
        if days_gap == 0:
            completed_daily = True
    if completed_daily:
        arr.append("task-daily")
    
    conn.commit()
    conn.close()
    resp = {"completed": arr}
    return JSONResponse(resp)

from aiogram.utils.deep_linking import decode_payload\

@dp.message_handler(commands=["start"])
async def handler(message: types.Message):
    refer_id = message.get_args()
    id = message.from_user.id
    name = str(message.from_user.first_name)
    last_name = str(message.from_user.last_name)
    if last_name != "None":
        name = name + f" {last_name}"
    args = message.get_args()
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    balance = cursor.execute(f"SELECT balance FROM users WHERE id = '{id}' ORDER BY balance DESC").fetchone()
    if balance == None or balance == (None) or balance == [None]:
        balance = 0
        cursor.execute(f"INSERT INTO users (id, username, balance, referal) VALUES ('{id}', '{name}', '0', '{refer_id}')")
    else:
        print()
    conn.commit()
    await message.reply("Hi! I'm your bot!")

@dp.message_handler(commands=['miniapp'])
async def open_miniapp(message: types.Message):
    markup = types.InlineKeyboardMarkup(resize_keyboard=True)
    webapp = types.WebAppInfo(url="https://andreyvsc.github.io/StudiesENGbot-test/main.html")
    button = types.InlineKeyboardButton("Open miniapp", web_app=webapp)
    markup.add(button)
    await message.reply("Open MiniApp:", reply_markup=markup)

import asyncio

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, skip_updates=False)

def start_app():
    uvicorn.run(app, host="andreybogdanov.ru", port=443,ssl_keyfile='/root/nginx-selfsigned.key', ssl_certfile='/root/nginx-selfsigned.crt')
    # uvicorn.run(app, host="45.82.153.57", port=80)

if __name__ == '__main__':
    # start_bot()
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
    start_app()