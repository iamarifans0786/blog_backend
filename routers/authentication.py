from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import models
from sqlalchemy.orm import Session
from database import get_db
from hashing import Hash
from JWTtoken import create_access_token
import schemas
from oauth2 import get_current_user

router = APIRouter(tags=["Authentication"])


# for the FastApi Swagger UI Login
@router.post(
    "/login", status_code=status.HTTP_201_CREATED, response_model=schemas.Token
)
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Creadentials"
        )
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect Password"
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# for the react app login
@router.post("/login/app", status_code=status.HTTP_200_OK)
def login(request: schemas.Login, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Creadentials"
        )
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect Password"
        )
    access_token = create_access_token(data={"sub": user.email})
    response = {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login Successfull",
        "success": True,
    }
    return response


@router.get("/user/profile", status_code=200, response_model=schemas.ShowUser)
def Profile(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    logedIn_user = (
        db.query(models.User).filter(models.User.email == current_user.email).first()
    )
    user = db.query(models.User).filter(models.User.id == logedIn_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not authenticated",
        )
    return user


@router.put("/user/update", status_code=status.HTTP_200_OK)
def Update_profile(
    request: schemas.UpdateUser,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    logedIn_user = (
        db.query(models.User).filter(models.User.email == current_user.email).first()
    )
    user = db.query(models.User).filter(models.User.id == logedIn_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )
    user.name = request.name
    if request.password:
        user.password = Hash.bcrypt(request.password)
    db.commit()
    response = {
        "details": user,
        "message": "Profile Updated Successfully",
        "success": True,
    }
    return response


@router.delete("/user/{id}/delete", status_code=status.HTTP_200_OK)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )

    for blog in user.blogs:
        for comment in blog.comments:
            db.delete(comment)
        db.delete(blog)

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
