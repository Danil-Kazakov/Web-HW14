from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    """
        Schema representing the base structure of a contact.

        Attributes:
            first_name (str): The first name of the contact.
            last_name (str): The last name of the contact.
        """

    first_name: str
    last_name: str


class ContactResponse(ContactBase):
    """
       Schema representing the response structure for a contact.

       Inherits:
           ContactBase: Base schema for a contact.

       Attributes:
           id (int): The unique identifier of the contact.
           email (str): The email address of the contact.
           phone_number (str): The phone number of the contact.
           another_info (None): Additional information about the contact (default: None).
       """
    id: int
    email: str
    phone_number: str
    another_info: None

class UserModel(BaseModel):
    """
        Schema representing the structure of a user.

        Attributes:
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str): The password of the user.
        """
    username: str
    email: str
    password: str

class UserDb(BaseModel):
    """
       Schema representing the database structure of a user.

       Attributes:
           id (int): The unique identifier of the user.
           username (str): The username of the user.
           email (str): The email address of the user.
           created_at (datetime): The datetime when the user was created.
           avatar (str): The URL of the user's avatar.
       """
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """
        Schema representing the response structure for a user.

        Attributes:
            user (UserDb): Details of the user.
            detail (str): Additional detail message (default: "User successfully created").
        """

    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
        Schema representing a token.

        Attributes:
            access_token (str): The access token.
            refresh_token (str): The refresh token.
            token_type (str): The type of token (default: "bearer").
        """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Schema representing a request for email confirmation.

    Attributes:
        email (EmailStr): The email address for confirmation.
    """
    email: EmailStr
