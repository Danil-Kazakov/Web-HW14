from typing import List
from db import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from models import Contacts, User
from schemas import ContactBase, ContactResponse, UserModel
from libgravatar import Gravatar


async def get_contacts(skip: int, limit: int, db: Session) -> List[Contacts]:
    """
    Retrieves a list of contacts with specified pagination parameters.

    Args:
        skip (int): Number of contacts to skip.
        limit (int): Maximum number of contacts to return.
        db (Session): Database session.

    Returns:
        List[Contacts]: List of contacts.
    """
    return db.query(Contacts).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, db: Session) -> Contacts:
    """
    Retrieves a single contact by its ID.

    Args:
        contact_id (int): ID of the contact to retrieve.
        db (Session): Database session.

    Returns:
        Contacts: The contact with the specified ID.
    """
    return db.query(Contacts).filter(Contacts.id == contact_id).first()


async def create_contact(body: ContactResponse, db: Session = Depends(get_db)) -> Contacts:
    """
    Creates a new contact.

    Args:
        body (ContactResponse): Data for the new contact.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        Contacts: The newly created contact.
    """
    contact_data = body.dict()
    contact = Contacts(**contact_data)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactResponse, db: Session) -> Contacts | None:
    """
    Updates an existing contact.

    Args:
        contact_id (int): ID of the contact to update.
        body (ContactResponse): Updated data for the contact.
        db (Session): Database session.

    Returns:
        Contacts | None: The updated contact, or None if the contact does not exist.
    """
    contact = db.query(Contacts).filter(Contacts.id == contact_id).first()
    if contact:
        for attr, value in body.dict(exclude_unset=True).items():
            setattr(contact, attr, value)
        db.commit()
        db.refresh(contact)

    return contact


async def delete_contact(contact_id: int, db: Session) -> Contacts | None:
    """
    Deletes a contact.

    Args:
        contact_id (int): ID of the contact to delete.
        db (Session): Database session.

    Returns:
        Contacts | None: The deleted contact, or None if the contact does not exist.
    """
    contact = db.query(Contacts).filter(Contacts.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user by their email address.

    Args:
        email (str): Email address of the user.
        db (Session): Database session.

    Returns:
        User: The user with the specified email address.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user.

    Args:
        body (UserModel): Data for the new user.
        db (Session): Database session.

    Returns:
        User: The newly created user.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates the refresh token for a user.

    Args:
        user (User): User for whom to update the token.
        token (str | None): New refresh token value.
        db (Session): Database session.
    """
    user.refresh_token = token
    db.commit()


async def get_contacts(skip: int, limit: int, db: Session, current_user: User) -> List[Contacts]:
    """
    Retrieves contacts belonging to a specific user with specified pagination parameters.

    Args:
        skip (int): Number of contacts to skip.
        limit (int): Maximum number of contacts to return.
        db (Session): Database session.
        current_user (User): User whose contacts are being retrieved.

    Returns:
        List[Contacts]: List of contacts belonging to the current user.
    """
    return db.query(Contacts).filter_by(user=current_user).offset(skip).limit(limit).all()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Marks a user's email as confirmed.

    Args:
        email (str): Email address of the user.
        db (Session): Database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Updates a user's avatar URL.

    Args:
        email (str): Email address of the user.
        url (str): New avatar URL.
        db (Session): Database session.

    Returns:
        User: The updated user.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
