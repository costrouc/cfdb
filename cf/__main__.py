import pathlib
import json

from cf import orm, schema

def ensure_channel(session, channel_name: str):
    channel = session.query(orm.Channel).filter(orm.Channel.name == channel_name).first()
    if channel is None:
        channel = orm.Channel(name=channel_name)
        session.add(channel)
        session.commit()
    return channel


def ensure_license(session, license_name: str):
    license = session.query(orm.License).filter(orm.License.name == license_name).first()
    if license is None:
        license = orm.License(name=license_name)
        session.add(license)
        session.commit()
    return license


def ensure_maintainer(session, maintainer_name: str):
    maintainer = session.query(orm.Maintainer).filter(orm.Maintainer.name == maintainer_name).first()
    if maintainer is None:
        maintainer = orm.Maintainer(github=maintainer_name)
        session.add(maintainer)
        session.commit()
    return maintainer


def ensure_environment_variable(session, key: str, value: str):
    env_var = session.query(orm.EnvironmentVariable).filter(
        orm.EnvironmentVariable.key == key,
        orm.EnvironmentVariable.value == value
    ).first()
    if env_var is None:
        env_var = orm.EnvironmentVariable(key=key, value=value)
        session.add(env_var)
        session.commit()
    return env_var


def ensure_filename(session, filename: str):
    filename_model = session.query(orm.Filename).filter(orm.Filename.name == filename).first()
    if filename_model is None:
        filename_model = orm.Filename(name=filename)
        session.add(filename_model)
        session.commit()
    return filename_model


def store_build_artifact(session, build_artifact: schema.BuildArtifact):
    channels = []
    for channel in build_artifact.about.channels:
        channels.append(ensure_channel(session, channel))

    license = ensure_license(session, build_artifact.about.license)

    maintainers = []
    for maintainer in build_artifact.about.recipe_maintainers:
        maintainers.append(ensure_maintainer(session, maintainer))

    filenames = []
    for filename in build_artifact.files:
        filenames.append(ensure_filename(session, filename))

    env_vars = []
    for key, value in build_artifact.about.env_vars.items():
        env_vars.append(ensure_environment_variable(session, key, value))

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
        license=license,
        license_family=build_artifact.about.license_family,
        license_file=build_artifact.about.license_file,
        root_pkgs=build_artifact.about.root_pkgs,
        summary=build_artifact.about.summary,
        tags=build_artifact.about.tags,
        conda_build_config=build_artifact.conda_build_config,
        files=filenames,
        index=build_artifact_index,
        metadata_version=build_artifact.metadata_version,
        name=build_artifact.name,
        raw_recipe=build_artifact.raw_recipe,
        rendered_recipe=build_artifact.rendered_recipe,
        version=build_artifact.version,
    )
    session.add(build_artifact_model)
    session.commit()


if __name__ == "__main__":
    session = orm.new_session_factory(url="sqlite:///database.sqlite")
    total_size = 0

    for i, path in enumerate(pathlib.Path(".").glob("*/artifacts/**/*.json")):
        if i > 10_000:
            break

        total_size += path.stat().st_size
        print(path)
        with path.open() as f:
            build_artifact = schema.BuildArtifact.parse_obj(json.load(f))
        store_build_artifact(session, build_artifact)
    print(total_size)
