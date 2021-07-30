import hashlib
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from hatch import api_client, config
from hatch.schema import FileSchema, IndexSchema


def get_sha(path):
    """Calculate and cache the sha256 hash of a file.

    We cache because a big workspace can have lots of large files, and serving
    the index would involve calculating the hashes of all files, which could get
    slow.

    We cache it in a separate directory, but the same relative path. So the
    cache for config.WORKSPACES/workspace1/output/file.txt is located at
    config.CACHE/workspace1/output/file.txt.
    """
    sha_path = config.CACHE / path.relative_to(config.WORKSPACES)
    sha = None
    # does cache file exist and is current?
    if sha_path.exists():
        sha_modified = sha_path.stat().st_mtime
        src_modified = path.stat().st_mtime
        if src_modified < sha_modified:
            sha = sha_path.read_text()

    if sha is None:
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        sha_path.parent.mkdir(parents=True, exist_ok=True)
        sha_path.write_text(sha)

    return sha


def get_files(path):
    """List all files in a directory recursively as a flat list.

    Sorted, and excluding various files
    """

    def exclude(p):
        strpath = str(p)
        return (
            strpath.startswith(".")
            or strpath.startswith("releases/")
            or strpath.startswith("metadata/")
            or str(p.name).startswith(".")
        )

    relative_paths = (p.relative_to(path) for p in path.glob("**/*") if p.is_file())
    return list(sorted(filter(lambda p: not exclude(p), relative_paths)))


def get_index(path, url_builder):
    files = []
    for name in get_files(path):
        abspath = path / name
        stat = abspath.stat()
        date = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        files.append(
            FileSchema(
                name=name,
                url=url_builder(filename=str(name)),
                size=stat.st_size,
                sha256=get_sha(abspath),
                date=date,
            )
        )
    return IndexSchema(files=files)


def validate_release(workspace, workspace_dir, release):
    """Validate the Release files are valid and match on sha."""
    errors = []

    for name, sha in release.files.items():
        p = workspace_dir / name
        if not p.exists():
            errors.append(f"File {name} not found in workspace {workspace}")
        elif sha != get_sha(p):
            errors.append(f"File {name} does not match sha of '{sha}'")

    return errors


def create_release(workspace, workspace_dir, release, user):
    """Create a Release on job-server.

    This involves copying the files to a tmpdir, and creating the Release
    in job-server. On success, the tmpdir is renamed to match the Release id
    returned from job-server.
    """
    # we use dir=config.CACHE as os.rename only works if on same filesystem,
    # and /tmp is usually a tmpfs
    tmpdir = tempfile.TemporaryDirectory(dir=config.CACHE)
    tmp = Path(tmpdir.name)
    try:
        # copy files to a temp dir
        copy_files(workspace_dir, release.files, tmp)

        # tell job-server about the files
        response = api_client.create_release(workspace, release, user)

        # copy file into releases subdir of workspace dir
        workspace_release_dir = workspace_dir / "releases"
        workspace_release_dir.mkdir(parents=True, exist_ok=True)
        # rename tempdir to match release id
        os.rename(tmp, workspace_release_dir / response.headers["Release-Id"])
    except Exception:
        tmpdir.cleanup()
        raise
    else:
        return response


def copy_files(srcdir, files, dstdir):
    """Copy files from srcdir to dstdir, ensuring dirs are created."""
    for f in files:
        src = srcdir / f
        dst = dstdir / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)


def upload_file(release_id, name, path, user):
    """Upload a file to job-server."""
    # this is really simple, there's nothing to except make the request
    return api_client.upload_file(release_id, name, path, user)
