from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# データベースセッションの依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize data on startup
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        crud.initialize_data(db)
    finally:
        db.close()

# Read 操作
@app.get("/users", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/rooms", response_model=List[schemas.Room])
async def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms

@app.get("/bookings", response_model=List[schemas.Booking])
async def read_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = crud.get_bookings(db, skip=skip, limit=limit)
    return bookings

# Create 操作
@app.post("/users", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.post("/rooms", response_model=schemas.Room)
async def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    return crud.create_room(db=db, room=room)

@app.post("/bookings", response_model=schemas.Booking)
async def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    return crud.create_booking(db=db, booking=booking)


# Update user
@app.put("/users/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Delete user
@app.delete("/users/{user_id}", response_model=schemas.User)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Update room
@app.put("/rooms/{room_id}", response_model=schemas.Room)
async def update_room(room_id: int, room: schemas.RoomUpdate, db: Session = Depends(get_db)):
    db_room = crud.update_room(db, room_id=room_id, room=room)
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

# Delete room
@app.delete("/rooms/{room_id}", response_model=schemas.Room)
async def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = crud.delete_room(db, room_id=room_id)
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

# Update booking
@app.put("/bookings/{booking_id}", response_model=schemas.Booking)
async def update_booking(booking_id: int, booking: schemas.BookingUpdate, db: Session = Depends(get_db)):
    db_booking = crud.update_booking(db, booking_id=booking_id, booking=booking)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking

# Delete booking
@app.delete("/bookings/{booking_id}", response_model=schemas.Booking)
async def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = crud.delete_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking