import typing

from pydantic import BaseModel, Field


class Base(BaseModel):
    class Config:
        extra = "forbid"


class BuildArtifactAbout(Base):
    channels: list[str] = []
    conda_build_version: str = None
    conda_env_version: str = None
    offline: bool = None
    conda_private: bool = None
    conda_version: str = None
    description: str = None
    dev_url: str = None
    doc_url: str = None
    doc_source_url: str = None
    env_vars: dict[str, str] = {}
    extra: typing.Any
    recipe_maintainers: list[str] = Field([], alias="recipe-maintainers")
    home: str = None
    identifiers: list[str] = []
    keywords: list[str] = []
    license: str = None
    license_family: str = None
    license_file: typing.Union[str, list[str]] = None
    license_url: str = None # ignored currently
    root_pkgs: list[typing.Any] = []
    summary: str = None
    tags: list[str] = []


class BuildArtifactIndex(Base):
    arch: str = None
    build: str
    build_number: int
    depends: list[str] = []
    constrains: list[str] = []
    features: str = None
    license: str = None
    license_family: str = None
    name: str
    noarch: str = None
    platform: str = None
    subdir: str
    timestamp: int = None
    version: str


class BuildArtifact(Base):
    about: BuildArtifactAbout
    conda_build_config: typing.Any
    conda_pkg_format: str = None # ignored currently
    files: list[str]
    index: BuildArtifactIndex
    metadata_version: int
    name: str
    raw_recipe: str
    rendered_recipe: dict
    version: str

    class Config:
        extra = 'forbid'
