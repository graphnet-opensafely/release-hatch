import os
from dataclasses import dataclass
from pathlib import Path

import pytest


# set a testing secret
os.environ["BACKEND_TOKEN"] = "secret"
os.environ["SERVER_HOST"] = "http://testserver"
import hatch.config  # noqa: E402


@dataclass
class Workspace:
    path: Path
    cache: Path
    root: Path

    def write(self, name, contents):
        path = self.path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
        return path


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    cache = tmp_path / "cache"
    releases = tmp_path / "releases"
    workspace.mkdir()
    cache.mkdir()
    releases.mkdir()
    monkeypatch.setattr(hatch.config, "WORKSPACES", tmp_path)
    monkeypatch.setattr(hatch.config, "CACHE", cache)
    monkeypatch.setattr(hatch.config, "RELEASES", releases)
    return Workspace(workspace, cache, tmp_path)
