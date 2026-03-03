"""Pydantic validation schemas."""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class RegisterSchema(BaseModel):
    """Registration request schema."""
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not v or "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address")
        if len(v) > 255:
            raise ValueError("Email too long")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        if len(v) > 128:
            raise ValueError("Password too long")
        return v


class LoginSchema(BaseModel):
    """Login request schema."""
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class RatingSchema(BaseModel):
    """Rating creation/update schema."""
    movie_id: int
    score: int
    movie_title: str = ""
    poster_path: Optional[str] = None

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Score must be between 1 and 5")
        return v

    @field_validator("movie_id")
    @classmethod
    def validate_movie_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Invalid movie ID")
        return v

    @field_validator("movie_title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        return v.strip()[:500]


class SearchQuerySchema(BaseModel):
    """Search query validation schema."""
    query: str = ""
    page: int = 1
    genre: Optional[int] = None
    year: Optional[int] = None

    @field_validator("page")
    @classmethod
    def validate_page(cls, v: int) -> int:
        if v < 1:
            return 1
        if v > 500:
            return 500
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1888 or v > 2030):
            raise ValueError("Invalid year")
        return v

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        return v.strip()[:200]
