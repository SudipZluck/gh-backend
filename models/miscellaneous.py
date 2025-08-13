from datetime import datetime
from typing import Optional, Annotated

from sqlmodel import SQLModel, Field, Relationship, table
from models.user import User
from models.journal import Journal


