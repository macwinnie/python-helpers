#!/usr/bin/env python3
from os import getcwd
from os import listdir
from os.path import isfile
from os.path import join
from pathlib import Path

import git
from tomlkit import dumps
from tomlkit import parse

from macwinnie_pyhelpers.Version import Version

curPath = getcwd()

pyprojectFile = Path(f"{curPath}/pyproject.toml")
pyproject = parse(pyprojectFile.read_text())
buildVersion = Version(pyproject["tool"]["poetry"]["version"])

tagVersions = [Version(str(t)) for t in git.Repo(getcwd()).tags]

distDir = join(curPath, "dist")
versionArchives = [
    Version(f.rsplit(".tar", 1)[0].rsplit("-", 1)[1])
    for f in listdir(distDir)
    if isfile(join(distDir, f)) and f.replace(".tar.gz", "") != f
]

if buildVersion in tagVersions or buildVersion in versionArchives:
    buildVersion.increase()
    pyproject["tool"]["poetry"]["version"] = str(buildVersion)
    with pyprojectFile.open(mode="w", encoding="utf-8") as file:
        file.write(dumps(pyproject))
        file.close()

versionFile = Path(f"{curPath}/.github.push.version")
with versionFile.open(mode="w", encoding="utf-8") as file:
    file.write(f"versiontag={buildVersion}")
    file.close()
