#!/usr/bin/env bash

apt-get update
apt-get -y install\
    jq xmlstarlet \
    python3-dev python3-wheel python3-distutils \
    tree

rm -rf "$( pwd )/Pipfile.lock"

pip install --user --upgrade \
    pip\
    pipenv\
    pipfile\
    twine

addPath="$( cd ~ || exit; pwd )/.local/bin"
export PATH="${addPath}:${PATH}"

pipenv install --dev

# export env variables to .env file
export DEBIAN_FRONTEND="noninteractive"
env | grep -E '^((TWINE)|(INC_VERSION)|(WD_PATH)|(DEBIAN_FRONTEND))' > "$(pwd)/.env"

# activate pipenv and build
chmod a+x "$( pwd )/wf_build.sh"
pipenv run bash -c "$( pwd )/wf_build.sh; exit"
# pipenv shell "$( pwd )/wf_build.sh; exit"
