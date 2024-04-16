from sqlalchemy import Column, Integer, String, Boolean, func, Table, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contacts(Base):
    """
        SQLAlchemy model representing the 'contacts' table.

        Attributes:
            __tablename__ (str): Name of the database table.
            id (int): Primary key for the table.
            first_name (str): First name of the contact.
            last_name (str): Last name of the contact.
            email (str): Email address of the contact.
            phone_number (int): Phone number of the contact.
            born_date (int): Date of birth of the contact.
            another_info (str): Additional information about the contact.
            user_id (int): Foreign key referencing the 'id' column of the 'users' table.
            user (relationship): Relationship with the 'User' model.

        """
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column(Integer)
    born_date = Column(Integer)
    another_info = Column(String, default=None)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="tags")




class User(Base):
    """
        SQLAlchemy model representing the 'users' table.

        Attributes:
            __tablename__ (str): Name of the database table.
            id (int): Primary key for the table.
            username (str): Username of the user.
            email (str): Email address of the user.
            password (str): Password of the user.
            created_at (DateTime): Timestamp indicating when the user was created.
            avatar (str): URL to the user's avatar image.
            refresh_token (str): Refresh token for the user.

        """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column("created_at", DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)


engine = create_engine('postgresql+psycopg2://postgres:567432@localhost:5432/hw')
Base.metadata.create_all(engine)
