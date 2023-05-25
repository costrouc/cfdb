import pathlib
import json
import functools
import sys

from tqdm import tqdm

from cf import orm, schema


def store_build_artifact(session, build_artifact_channel: str, build_artifact: schema.BuildArtifact):
    @functools.cache
    def ensure_channel(channel_name: str):
        channel = session.query(orm.Channel).filter(orm.Channel.name == channel_name).first()
        if channel is None:
            channel = orm.Channel(name=channel_name)
            session.add(channel)
            session.commit()
        return channel

    @functools.cache
    def ensure_license(license_name: str):
        license = session.query(orm.License).filter(orm.License.name == license_name).first()
        if license is None:
            license = orm.License(name=license_name)
            session.add(license)
            session.commit()
        return license.id

    @functools.cache
    def ensure_maintainer(maintainer_name: str):
        maintainer = session.query(orm.Maintainer).filter(orm.Maintainer.name == maintainer_name).first()
        if maintainer is None:
            maintainer = orm.Maintainer(github=maintainer_name)
            session.add(maintainer)
            session.commit()
        return maintainer

    @functools.cache
    def ensure_environment_variable(key: str, value: str):
        env_var = session.query(orm.EnvironmentVariable).filter(
            orm.EnvironmentVariable.key == key,
            orm.EnvironmentVariable.value == value
        ).first()
        if env_var is None:
            env_var = orm.EnvironmentVariable(key=key, value=value)
            session.add(env_var)
            session.commit()
        return env_var

    @functools.cache
    def ensure_inode(name: str, parent_id: int):
        inode = session.query(orm.INode).filter(
            orm.INode.parent_id == parent_id,
            orm.INode.name == name
        ).first()
        if inode is None:
            inode = orm.INode(
                parent_id=parent_id,
                name=name
            )
            session.add(inode)
            session.commit()
        return inode.id

    @functools.cache
    def ensure_filename(filename: str):
        path = pathlib.Path(filename)
        parent_id = None
        for name in path.parts:
            parent_id = ensure_inode(name=name, parent_id=parent_id)
        return parent_id

    build_artifact_channel_model = ensure_channel(build_artifact_channel)

    if session.query(orm.BuildArtifact).join(
        orm.BuildArtifact.index
    ).filter(
        orm.BuildArtifact.channel_id == build_artifact_channel_model.id,
        orm.BuildArtifactIndex.subdir == build_artifact.index.subdir,
        orm.BuildArtifactIndex.name == build_artifact.index.name,
        orm.BuildArtifactIndex.version == build_artifact.index.version,
        orm.BuildArtifactIndex.build == build_artifact.index.build,
    ).first() is not None:
        # print(f'SKIPPING {build_artifact_channel}/{build_artifact.index.subdir}/{build_artifact.index.name}-{build_artifact.index.version}-{build_artifact.index.build}')
        return

    channels = []
    for channel in build_artifact.about.channels:
        channels.append(ensure_channel(channel))

    license_id = ensure_license(build_artifact.about.license)

    maintainers = []
    for maintainer in build_artifact.about.recipe_maintainers:
        maintainers.append(ensure_maintainer(maintainer))

    env_vars = []
    for key, value in build_artifact.about.env_vars.items():
        env_vars.append(ensure_environment_variable(key, value))

    build_artifact_index = orm.BuildArtifactIndex(
        arch=build_artifact.index.arch,
        build=build_artifact.index.build,
        build_number=build_artifact.index.build_number,
        depends=build_artifact.index.depends,
        constrains=build_artifact.index.constrains,
        features=build_artifact.index.features,
        license=build_artifact.index.license,
        license_family=build_artifact.index.license_family,
        name=build_artifact.index.name,
        noarch=build_artifact.index.noarch,
        platform=build_artifact.index.platform,
        subdir=build_artifact.index.subdir,
        timestamp=build_artifact.index.timestamp,
        version=build_artifact.index.version,
    )
    session.add(build_artifact_index)
    session.commit()

    build_artifact_model = orm.BuildArtifact(
        channel=build_artifact_channel_model,
        channels=channels,
        conda_build_version=build_artifact.about.conda_build_version,
        conda_private=build_artifact.about.conda_private,
        conda_env_version=build_artifact.about.conda_env_version,
        conda_version=build_artifact.about.conda_version,
        description=build_artifact.about.description,
        dev_url=build_artifact.about.dev_url,
        doc_url=build_artifact.about.doc_url,
        doc_source_url=build_artifact.about.doc_source_url,
        env_vars=env_vars,
        extra=build_artifact.about.extra,
        recipe_maintainers=maintainers,
        offline=build_artifact.about.offline,
        home=build_artifact.about.home,
        identifiers=build_artifact.about.identifiers,
        keywords=build_artifact.about.keywords,
        license_id=license_id,
        license_family=build_artifact.about.license_family,
        license_file=build_artifact.about.license_file,
        root_pkgs=build_artifact.about.root_pkgs,
        summary=build_artifact.about.summary,
        tags=build_artifact.about.tags,
        conda_build_config=build_artifact.conda_build_config,
        index=build_artifact_index,
        metadata_version=build_artifact.metadata_version,
        name=build_artifact.name,
        raw_recipe=build_artifact.raw_recipe,
        rendered_recipe=build_artifact.rendered_recipe,
        version=build_artifact.version,
    )
    session.add(build_artifact_model)
    session.commit()

    filenames = []
    for filename in build_artifact.files:
        inode_id = ensure_filename(filename)
        inodemetadata = orm.INodeMetadata(inode_id=inode_id, buildartifact_id=build_artifact_model.id)
        session.add(inodemetadata)
    session.commit()


if __name__ == "__main__":
    database_filename = 'database.sqlite'

    session = orm.new_session_factory(url=f"sqlite:///{database_filename}")
    total_size = 0
    database_size = 0

    directory = sys.argv[1]

    paths = tqdm(list(pathlib.Path(directory).glob("artifacts/*/*/*/*.json")))
    for i, path in enumarate(paths):
        package_name, channel, subdir, filename = path.parts[-4:]

        total_size += path.stat().st_size
        database_size = pathlib.Path(database_filename).stat().st_size

        paths.set_description(f'Efficiency {database_size / total_size:0.2f} [%] Database {database_size // 1024**2} [MB] Files {total_size // 1024**2} [MB]')
        paths.refresh()

        with path.open() as f:
            build_artifact = schema.BuildArtifact.parse_obj(json.load(f))
        store_build_artifact(session, channel, build_artifact)
    print(total_size)
