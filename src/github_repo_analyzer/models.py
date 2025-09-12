"""Data models for GitHub Repository Analyzer."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class Owner(BaseModel):
    """GitHub repository owner model."""

    login: str
    id: int
    type: str
    html_url: str
    avatar_url: str


class Repository(BaseModel):
    """Strongly typed Repository model using Pydantic."""

    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    clone_url: str
    ssh_url: str
    language: Optional[str] = None
    stargazers_count: int = Field(alias="stargazers_count")
    forks_count: int = Field(alias="forks_count")
    open_issues_count: int = Field(alias="open_issues_count")
    size: int
    created_at: str
    updated_at: str
    pushed_at: Optional[str] = None
    private: bool = False
    archived: bool = False
    disabled: bool = False
    topics: List[str] = Field(default_factory=list)
    license: Optional[Dict[str, Any]] = None
    owner: Owner

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def format_datetime(cls, v: Any) -> Any:
        """Format datetime objects to ISO strings."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    @field_validator("pushed_at", mode="before")
    @classmethod
    def format_pushed_at(cls, v: Any) -> Any:
        """Format pushed_at datetime to ISO string or None."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    @classmethod
    def from_pygithub(cls, repo: Any) -> "Repository":
        """Create Repository from PyGithub object - DRY approach."""
        # Use Pydantic's model_validate with a dictionary comprehension
        # This automatically handles field mapping and validation
        data = {
            # Direct field mapping
            field: getattr(repo, field)
            for field in [
                "name",
                "full_name",
                "description",
                "html_url",
                "clone_url",
                "ssh_url",
                "language",
                "stargazers_count",
                "forks_count",
                "open_issues_count",
                "size",
                "private",
                "archived",
                "disabled",
            ]
            if hasattr(repo, field)
        }

        # Add datetime fields (validators will handle formatting)
        data.update(
            {
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
                "pushed_at": repo.pushed_at,
            }
        )

        # Add owner (let Pydantic handle validation)
        data["owner"] = {
            "login": repo.owner.login,
            "id": repo.owner.id,
            "type": repo.owner.type,
            "html_url": repo.owner.html_url,
            "avatar_url": repo.owner.avatar_url,
        }

        # Add defaults
        data.update(
            {
                "topics": [],  # Skip to avoid extra API calls
                "license": None,  # Skip to avoid extra API calls
            }
        )

        return cls.model_validate(data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Repository to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the repository
        """
        return self.model_dump()
