from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, UploadFile, File
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session
from db import get_db
import repository as repository_contacts
from models import User
from schemas import ContactResponse, UserResponse, UserModel, TokenModel, RequestEmail
from typing import List
from auth import auth_service
import repository as repository_users
from my_email import send_email
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import cloudinary
import cloudinary.uploader
from schemas import UserDb
from config import settings





app = APIRouter(prefix='/contacts', tags=["contacts"])
router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()




@app.get('/', response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
        Retrieve a list of contacts with specified pagination parameters.

        Args:
            skip (int): Number of contacts to skip.
            limit (int): Maximum number of contacts to return.
            db (Session): Database session.

        Returns:
            List[ContactResponse]: List of contacts.
        """
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    return contacts


@app.get('/{contact_id}', response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single contact by its ID.

    Args:
        contact_id (int): ID of the contact to retrieve.
        db (Session): Database session.

    Returns:
        ContactResponse: The contact with the specified ID.
    """

    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@app.post("/", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: ContactResponse, db: Session = Depends(get_db)):
    """
        Create a new contact.

        Args:
            body (ContactResponse): Data for the new contact.
            db (Session): Database session.

        Returns:
            ContactResponse: The newly created contact.
        """
    return await repository_contacts.create_contact(body, db)


@app.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactResponse, contact_id: int, db: Session = Depends(get_db)):
    """
            Update a contact.

            Args:
                body (ContactResponse): Data for the new contact.
                db (Session): Database session.

            Returns:
                ContactResponse: The new updated contact.
            """
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@app.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """
                Delete a contact.

                Args:
                    body (ContactResponse): Data for the new contact.
                    db (Session): Database session.

                Returns:
                    ContactResponse: The deleted contact.
                """
    contact = await repository_contacts.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
        Sign up a new user.

        Args:
            body (UserModel): Data for the new user.
            background_tasks (BackgroundTasks): Background tasks to be executed.
            request (Request): Incoming request.
            db (Session): Database session.

        Returns:
            UserResponse: Details of the newly created user.
        """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
            Login a user.

            Args:
                body (UserModel): Data for the new user.
                db (Session): Database session.

            Returns:
                UserResponse: Tokens type.
            """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
        Refresh the access token using the refresh token.

        Args:
            credentials (HTTPAuthorizationCredentials): HTTP Authorization credentials containing the refresh token.
            db (Session): Database session.

        Returns:
            TokenModel: New access token and refresh token.
        """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.get('/', response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
        Retrieve a list of contacts associated with the current user.

        Args:
            skip (int): Number of contacts to skip.
            limit (int): Maximum number of contacts to return.
            db (Session): Database session.
            current_user (User): Current authenticated user.

        Returns:
            List[ContactResponse]: List of contacts.
        """

    contacts = await repository_contacts.get_contacts(skip, limit, db, current_user)
    return contacts


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
        Confirm the email address associated with the provided token.

        Args:
            token (str): Token for email confirmation.
            db (Session): Database session.

        Returns:
            dict: Confirmation message.
        """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}



@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    Request email confirmation.

    Args:
        body (RequestEmail): Request body containing the email address.
        background_tasks (BackgroundTasks): Background tasks to be executed.
        request (Request): Incoming request.
        db (Session): Database session.

    Returns:
        dict: Confirmation message.
    """

    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}



@app.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
        Get details of the current user.

        Args:
            current_user (User): Current authenticated user.

        Returns:
            UserDb: Details of the current user.
        """
    return current_user


@app.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    Update the avatar of the current user.

    Args:
        file (UploadFile): Uploaded file containing the new avatar image.
        current_user (User): Current authenticated user.
        db (Session): Database session.

    Returns:
        UserDb: Details of the updated user.
    """

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user