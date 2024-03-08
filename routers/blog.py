from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, Form
from typing import List
from sqlalchemy.orm import Session
from database import get_db
import schemas
import models
import os
import uuid
from fastapi.staticfiles import StaticFiles
from oauth2 import get_current_user

router = APIRouter(prefix="/blog", tags=["Blogs"])


# Create a directory to store uploaded files
UPLOAD_DIR = "static/image"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Function to generate random name for image file
def generate_random_name(filename: str) -> str:
    random_name = str(uuid.uuid4())  # Generate UUID
    _, ext = os.path.splitext(filename)  # Get file extension
    return random_name + ext


@router.post("/", status_code=status.HTTP_201_CREATED)
async def Create(
    title: str = Form(...),
    subtitle: str = Form(...),
    desc: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    print(image)
    random_filename = generate_random_name(image.filename)
    file_path = os.path.join(UPLOAD_DIR, random_filename)
    with open(file_path, "wb") as f:
        f.write(image.file.read())
    logedIn_user = (
        db.query(models.User).filter(models.User.email == current_user.email).first()
    )
    new_blog = models.Blog(
        title=title,
        subtitle=subtitle,
        desc=desc,
        image=file_path,
        user_id=logedIn_user.id,
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    response = {
        "data": new_blog,
        "message": "data created successfully",
        "success": True,
    }
    return response


@router.get(
    "/all", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowBlog]
)
def All(
    db: Session = Depends(get_db),
):
    blogs = db.query(models.Blog).all()
    for blog in blogs:
        blog.image = "http://localhost:8000/" + blog.image.replace("\\", "/")
    return blogs


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowBlog])
def blogs(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    logedIn_user = (
        db.query(models.User).filter(models.User.email == current_user.email).first()
    )
    blogs = db.query(models.Blog).filter(models.Blog.user_id == logedIn_user.id).all()
    for blog in blogs:
        blog.image = "http://localhost:8000/" + blog.image.replace("\\", "/")
    return blogs


@router.get(
    "/{id}", status_code=200, response_model=schemas.ShowBlog
)  # using the respnse model for returning blogs data
def show_blog(
    id: int,
    db: Session = Depends(get_db),
):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with the id {id} is not available",
        )

    blog.image = "http://localhost:8000/" + blog.image.replace("\\", "/")
    return blog


@router.put("/{id}/update", status_code=status.HTTP_202_ACCEPTED)
def update(
    id: int,
    title: str = Form(None),
    subtitle: str = Form(None),
    desc: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    logged_in_user = (
        db.query(models.User).filter(models.User.email == current_user.email).first()
    )
    request_dict = {}

    if title is not None:
        request_dict["title"] = title
    if subtitle is not None:
        request_dict["subtitle"] = subtitle
    if desc is not None:
        request_dict["desc"] = desc

    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with the id {id} is not available",
        )
    if blog.user_id == logged_in_user.id:
        if image:
            random_filename = generate_random_name(image.filename)
            file_path = os.path.join(UPLOAD_DIR, random_filename)
            with open(file_path, "wb") as f:
                f.write(image.file.read())
            request_dict["image"] = file_path

        for key, value in request_dict.items():
            setattr(blog, key, value)

        db.commit()
        return {
            "data": request_dict,
            "message": "Data updated successfully",
            "success": True,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this blog",
        )


@router.delete("/{id}/delete", status_code=status.HTTP_200_OK)
def Destroy(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    logged_in_user = (
        db.query(models.User).filter(models.User.email == current_user.email).first()
    )
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with the id {id} is not available",
        )
    if blog.user_id == logged_in_user.id:
        db.delete(blog)
        db.commit()
        return {"message": "Data deleted successfully", "success": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this blog",
        )
