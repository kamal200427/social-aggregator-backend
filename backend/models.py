# ./backend/models.py

from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
    """
    Database model for a social media post.
    Supports YouTube, Twitter, LinkedIn, Instagram, and Facebook.
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50))
    source_channel = Column(String, nullable=True)
    author = Column(String(200))
    title = Column(String(500))
    url = Column(String(1000), unique=True)
    timestamp = Column(DateTime)
    content = Column(Text)
    media = Column(String(1000))
    thumbnail = Column(String(1000)) 

class UserSource(Base):
    __tablename__ = "user_sources"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)   # e.g. "youtube", "facebook"
    url = Column(String, unique=True)       # e.g. pasted link
class Register(Base):
    __tablename__ = "user_register"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))  # e.g. "youtube", "facebook" 
    email= Column(String(200))
    username= Column(String(200))
    password= Column(String(200))