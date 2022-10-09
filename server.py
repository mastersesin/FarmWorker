import math
import os
import time
from typing import Optional

import sqlalchemy
from pydantic import BaseModel

import database

import uvicorn
from database import engine, get_db
from fastapi import Depends, FastAPI, Response, status
from sqlalchemy.orm import Session
import uuid

database.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Item(BaseModel):
    rclone_token_id: str
    folder_id: str
    worker_id: str


class HealthCheck(BaseModel):
    worker_id: str


def get_all_folder(db: Session):
    return db.query(database.Folder).all()


def get_all_token(db: Session):
    return db.query(database.Token).all()


def get_all_worker(db: Session):
    return_list = []
    records = db.query(database.Worker).all()
    for record in records:
        return_list.append(
            {**record.__dict__, "last_activity": math.ceil((int(time.time()) - int(record.last_activity)) / 60)})
    return return_list


def create_Folder(db: Session, folder_id: str):
    db_Data = database.Folder(folder_id=folder_id)
    db.add(db_Data)
    db.commit()
    db.refresh(db_Data)
    return db_Data


def create_Token(db: Session, rclone_token: str, client_id: str, client_secret: str):
    db_Data = database.Token(rclone_token=rclone_token, client_id=client_id, client_secret=client_secret)
    db.add(db_Data)
    db.commit()
    db.refresh(db_Data)
    return db_Data


def check_data_exist_folder(db: Session, folder_id: str):
    data1 = db.query(database.Folder).filter(database.Folder.folder_id == folder_id).first()
    return data1


def check_data_exist_token(db: Session, rclone_token: str):
    data1 = db.query(database.Token).filter(database.Token.rclone_token == rclone_token).first()
    return data1


def check_data_unused_folder(db: Session):
    data = db.query(database.Folder). \
        outerjoin(database.Worker, database.Worker.folder_id == database.Folder.id). \
        filter(database.Worker.id.is_(None)).all()
    return data


def check_data_unused_token(db: Session):
    data = db.query(database.Token). \
        outerjoin(database.Worker, database.Worker.token_id == database.Token.id). \
        filter(database.Worker.id.is_(None)).all()
    return data


def update_last_activity_time(db: Session, worker_id: str):
    data = db.query(database.Worker). \
        filter(database.Worker.worker_id == worker_id). \
        update({"last_activity": int(time.time())})
    db.commit()
    return data


def add_new_worker(db: Session, folder_id: str, rclone_id: str, worker_id: str):
    folder_obj = db.query(database.Folder).filter(database.Folder.id == folder_id).first()
    if not folder_obj:
        return {"status": False, "reason": f"Folder id {folder_id} not exist"}
    token_obj = db.query(database.Token).filter(database.Token.id == rclone_id).first()
    if not token_obj:
        return {"status": False, "reason": f"Rclone id {rclone_id} not exist"}
    new_worker_obj = database.Worker(
        folder_id=folder_obj.id,
        token_id=token_obj.id,
        worker_id=worker_id
    )
    db.add(new_worker_obj)
    db.commit()
    db.refresh(new_worker_obj)
    return {"status": True}


@app.get("/folder")
def read_folders(db: Session = Depends(get_db), is_filter: Optional[bool] = False):
    if is_filter:
        return {"status": True, "message": check_data_unused_folder(db=db)}
    else:
        return {"status": True, "message": get_all_folder(db=db)}


@app.get("/token")
def read_tokens(db: Session = Depends(get_db), is_filter: Optional[bool] = False):
    if is_filter:
        return {"status": True, "message": check_data_unused_token(db=db)}
    else:
        return {"status": True, "message": get_all_token(db=db)}


@app.get("/worker")
def read_tokens(db: Session = Depends(get_db)):
    return get_all_worker(db=db)


@app.post("/folder")
def create_folder(folder_id: str, db: Session = Depends(get_db)):
    check_exist_folder = check_data_exist_folder(db=db, folder_id=folder_id)
    if check_exist_folder:
        return {f"Error: folder_id {folder_id} is exist!"}
    data_data = create_Folder(db=db, folder_id=folder_id)
    return data_data


@app.post("/token")
def create_token(rclone_token: str, client_id: str, client_secret: str,
                 db: Session = Depends(get_db), response: Response = status.HTTP_201_CREATED):
    check_exist_folder = check_data_exist_token(db=db, rclone_token=rclone_token)
    if check_exist_folder:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {f"Error: rclone_token {rclone_token} is exist!"}
    data = create_Token(db=db, rclone_token=rclone_token, client_id=client_id, client_secret=client_secret)
    return data


@app.post("/worker")
def map_folder_token(item: Item, db: Session = Depends(get_db)):
    try:
        add_f_t = add_new_worker(db=db, folder_id=item.folder_id, worker_id=item.worker_id,
                                 rclone_id=item.rclone_token_id)
        return add_f_t
    except sqlalchemy.exc.IntegrityError as e:
        return {"status": False, "message": e}


@app.put("/worker")
def health_check(data: HealthCheck, db: Session = Depends(get_db)):
    update_last_activity_time(db=db, worker_id=data.worker_id)
    return {"status": True}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.0", port=8002, reload=True)
