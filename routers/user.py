from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
import schemas
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from database import get_db
from hashing import Hash
from oauth2 import get_current_user

router = APIRouter(prefix="/user", tags=["Users"])


from fastapi import HTTPException


@router.post("/", status_code=status.HTTP_201_CREATED)
def Create(request: schemas.User, db: Session = Depends(get_db)):
    existing_user = (
        db.query(models.User).filter(models.User.email == request.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
    new_user = models.User(
        name=request.name, email=request.email, password=Hash.bcrypt(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    response = {
        "data": new_user,
        "message": "User Created Successfully",
        "success": True,
    }

    return response


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowUser])
def All(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.get("/{id}", status_code=200, response_model=schemas.ShowUser)
def show_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the id {id} is not available",
        )
    return user
