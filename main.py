from fastapi import FastAPI

from cn_subject import cn
from dbms_subject import dbms
from os_subject import os

app = FastAPI()

app.include_router(cn.router,
                   prefix="/cn",
                   tags=["Computer Networks"])

app.include_router(dbms.router,
                   prefix="/dbms",
                   tags=["DBMS"])

app.include_router(os.router,
                   prefix="/os",
                   tags=["OS"])

@app.get("/")
async def root():
    return {
        "message": "WOO-HOO!! Server UP!"
    }

