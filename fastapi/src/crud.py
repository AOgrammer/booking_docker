from fastapi import HTTPException
from sqlalchemy.orm import Session
import models, schemas
import datetime

def initialize_data(db: Session):
    # Check if initial data already exists
    if db.query(models.User).first() or db.query(models.Room).first() or db.query(models.Booking).first():
        return

    # Add users
    user = models.User(username="あおい")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Add rooms
    room = models.Room(room_name="会議室A", capacity=10)
    db.add(room)
    db.commit()
    db.refresh(room)

    # Add bookings
    booking = models.Booking(
        user_id=user.user_id,
        room_id=room.room_id,
        booked_num=5,
        start_datetime=datetime.datetime.now(),
        end_datetime=datetime.datetime.now() + datetime.timedelta(hours=1)
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

# ユーザー一覧取得
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# 会議室一覧取得
def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Room).offset(skip).limit(limit).all()

# 予約一覧取得
def get_bookings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).offset(skip).limit(limit).all()

# ユーザー登録
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 会議室登録
def create_room(db: Session, room: schemas.RoomCreate):
    db_room = models.Room(room_name=room.room_name, capacity=room.capacity)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

# 予約登録
def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booked = db.query(models.Booking).\
        filter(models.Booking.room_id == booking.room_id).\
        filter(models.Booking.end_datetime > booking.start_datetime).\
        filter(models.Booking.start_datetime < booking.end_datetime).\
        all()
    # 重複するデータがなければ
    if len(db_booked) == 0:
        db_booking = models.Booking(
            user_id = booking.user_id,
            room_id = booking.room_id,
            booked_num = booking.booked_num,
            start_datetime = booking.start_datetime,
            end_datetime = booking.end_datetime
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    else:
        raise HTTPException(status_code=404, detail="Already booked")

# User update
def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        return None
    db_user.username = user.username
    db.commit()
    db.refresh(db_user)
    return db_user

# User delete
def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

# Room update
def update_room(db: Session, room_id: int, room: schemas.RoomUpdate):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if db_room is None:
        return None
    db_room.room_name = room.room_name
    db_room.capacity = room.capacity
    db.commit()
    db.refresh(db_room)
    return db_room

# Room delete
def delete_room(db: Session, room_id: int):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if db_room is None:
        return None
    db.delete(db_room)
    db.commit()
    return db_room

# Booking update
def update_booking(db: Session, booking_id: int, booking: schemas.BookingUpdate):
    db_booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if db_booking is None:
        return None
    db_booking.user_id = booking.user_id
    db_booking.room_id = booking.room_id
    db_booking.booked_num = booking.booked_num
    db_booking.start_datetime = booking.start_datetime
    db_booking.end_datetime = booking.end_datetime
    db.commit()
    db.refresh(db_booking)
    return db_booking

# Booking delete
def delete_booking(db: Session, booking_id: int):
    db_booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if db_booking is None:
        return None
    db.delete(db_booking)
    db.commit()
    return db_booking