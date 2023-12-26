#!/usr/bin/env bash

set -ex

curPath="$( pwd )"

###
## prepare environment for further steps
###

# export env variables to .env file
export DEBIAN_FRONTEND="noninteractive"
env | grep -E '^((TWINE)|(INC_VERSION)|(WD_PATH)|(DEBIAN_FRONTEND))' > "$(pwd)/.env"

# allow git actions in
git config --global --add safe.directory "${curPath}"

# add and enable pyenv
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
export PATH=~/.pyenv/bin:$PATH
eval "$( pyenv init - )"

# update system
apt update
apt upgrade -y
apt install -y \
    virtualenv \
    python3-dev python3-wheel python3-distutils

# enable local venv
# shellcheck disable=SC1091
source .envrc

###
## ensure all repository criterias are met – so run
###
pre-commit autoupdate && git add -A
pre-commit run --all-files


###
## Handle Documentation
###

docPath="docs"
export docPath

# delete old documentation files
rm -rf "${docPath}" || true
mkdir -p "${docPath}"

# write out documentation for all python classes in src folder
pdoc macwinnie_pyhelpers --docformat google --output-dir "${docPath}"

#  update index page of documentation by current date and author information
chmod a+x wf_adjust_pdoc.py
python wf_adjust_pdoc.py

cd "${curPath}"


###
## Gather version to be published
###
chmod a+x wf_versionize.py
python wf_versionize.py


###
## Publish package
###

# build python library
python3 -m build

# upload to PyPI
twine upload dist/*


exit 0
