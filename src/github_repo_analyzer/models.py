"""Data models for GitHub Repository Analyzer."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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

    def to_dict(self) -> Dict[str, Any]:
        """Convert Repository to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the repository
        """
        return self.model_dump()
