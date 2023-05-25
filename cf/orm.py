from sqlalchemy import create_engine

from sqlalchemy import (
    Table,
    Boolean,
    Column,
    BigInteger,
    Integer,
    Unicode,
    Text,
    JSON,
    Enum,
    DateTime,
    UniqueConstraint,
    ForeignKey,
    UnicodeText,
    or_,
    and_,
)
from sqlalchemy.orm import (
    sessionmaker,
    relationship,
    scoped_session,
    backref,
    declarative_base,
)


Base = declarative_base()


class Channel(Base):
    __tablename__ = "channel"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True, index=True)


class Maintainer(Base):
    __tablename__ = "maintainer"

    id = Column(Integer, primary_key=True)
    github = Column(Unicode, unique=True, index=True)


class License(Base):
    __tablename__ = "license"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)


class INode(Base):
    __tablename__ = "inode"
    __table_args__ = (
        UniqueConstraint('parent_id', 'name'),
    )

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("inode.id"), nullable=True)
    name = Column(Unicode)


class INodeMetadata(Base):
    __tablename__ = "inodemetadata"

    inode_id = Column(Integer, ForeignKey("inode.id"), primary_key=True)
    buildartifact_id = Column(Integer, ForeignKey("buildartifact.id"), primary_key=True)


class EnvironmentVariable(Base):
    __tablename__ = "environmentvariable"

    id = Column(Integer, primary_key=True)

    key = Column(Unicode)
    value = Column(Unicode)


buildartifact_channel = Table(
    "buildartifact_channel",
    Base.metadata,
    Column("channel_id", ForeignKey("channel.id"), primary_key=True),
    Column(
        "artifact_id",
        ForeignKey("buildartifact.id"),
        primary_key=True,
    ),
)

buildartifact_maintainer = Table(
    "buildartifact_maintainer",
    Base.metadata,
    Column(
        "buildartifact_id",
        ForeignKey("buildartifact.id"),
        primary_key=True,
    ),
    Column(
        "maintainer_id",
        ForeignKey("maintainer.id"),
        primary_key=True,
    ),
)

buildartifact_environmentvariable = Table(
    "buildartifact_environmentvariable",
    Base.metadata,
    Column("environmentvariable_id", ForeignKey("environmentvariable.id"), primary_key=True),
    Column(
        "artifact_id",
        ForeignKey("buildartifact.id"),
        primary_key=True,
    ),
)


class BuildArtifactIndex(Base):
    __tablename__ = "buildartifactindex"

    id = Column(Integer, primary_key=True)

    arch = Column(Unicode, nullable=True)
    build = Column(Integer)
    build_number = Column(Integer)
    depends = Column(JSON)
    constrains = Column(JSON)
    features = Column(Unicode, nullable=True)
    license = Column(Unicode)
    license_family = Column(Unicode)
    name = Column(Unicode)
    noarch = Column(Unicode, nullable=True)
    platform = Column(Unicode, nullable=True)
    subdir = Column(Unicode)
    timestamp = Column(Integer, nullable=True)
    version = Column(Unicode)


class BuildArtifact(Base):
    __tablename__  = "buildartifact"

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("channel.id"), nullable=False)
    channel = relationship(Channel)

    ### ABOUT ###

    channels = relationship(Channel, secondary=buildartifact_channel)
    conda_build_version = Column(Unicode)
    conda_env_version = Column(Unicode, nullable=True)
    conda_private = Column(Boolean)
    conda_version = Column(Unicode)
    description = Column(Unicode, nullable=True)
    dev_url = Column(Unicode, nullable=True)
    doc_url = Column(Unicode, nullable=True)
    doc_source_url = Column(Unicode, nullable=True)
    env_vars = relationship(EnvironmentVariable, secondary=buildartifact_environmentvariable)

    extra = Column(JSON)

    recipe_maintainers = relationship(Maintainer, secondary=buildartifact_maintainer)

    offline = Column(Boolean, nullable=True)
    home = Column(Unicode, nullable=True)
    identifiers = Column(JSON)
    keywords = Column(JSON)

    license_id = Column(Integer, ForeignKey("license.id"), nullable=True)
    license = relationship(License)

    license_family = Column(Unicode, nullable=True)
    license_file = Column(JSON, nullable=True)

    root_pkgs = Column(JSON)

    summary = Column(Unicode, nullable=True)
    tags = Column(JSON)

    conda_build_config = Column(JSON)

    files = relationship(INodeMetadata)

    index_id = Column(Integer, ForeignKey("buildartifactindex.id"), nullable=False)
    index = relationship(BuildArtifactIndex)

    metadata_version = Column(Integer)

    name = Column(Unicode)
    raw_recipe = Column(Unicode)
    rendered_recipe = Column(JSON)
    version = Column(Unicode)


def new_session_factory(url="sqlite:///:memory:", reset=False, **kwargs):
    engine = create_engine(url, **kwargs)

    Base.metadata.create_all(engine)

    session_factory = scoped_session(sessionmaker(bind=engine))
    return session_factory
