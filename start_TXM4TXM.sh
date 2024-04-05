#!/usr/bin/env bash

set -efaou pipefail

source .env_txm4txm > /dev/null 2>&1

set +a

if [ "$TREETAGGER_HOME" ]
then

    echo "TREETAGGER_HOME is set to '$TREETAGGER_HOME'"
else
    echo "TREETAGGER_HOME is not set, if you continue, only the spaCy model will be available"
    read -p "Continue? [ y / $(tput setaf 1)N$(tput sgr0) ] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        echo "Aborting"
        exit 1
    else
        echo "Caution, no output will be saved"
    fi
fi


cd "${FOLDER:=`pwd`/}"

# Ensure pwd has worked
if [ -z "${FOLDER%/*}" ]
then
    echo "The pwd command failed, leading to cd to $FOLDER"
    exit 1
fi

# git pull origin master --quiet || exit

if [ ! -d "venv" ]
then
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

source "$FOLDER"/"venv/bin/activate"

# Ensure that we have everything we need
for package in `cat requirements.txt`
do
    if $(echo $package | grep -q '@https://')
    then
        echo "Skipping $package"
        continue
    fi
    if ! pip show $package > /dev/null
    then
        echo "Missing $package, trying to install it..."
        pip install $package
    fi
done


COMMAND="source $FOLDER""venv/bin/activate; python -m uvicorn src.main:app --host ${TXM4TXM_HOST:-'0.0.0.0'} --port ${TXM4TXM_PORT:-'8000'} --root-path ${ROOT_PATH:-'/'} --workers 4 --timeout-keep-alive 1000 --log-config log.conf"

printf "Starting txm4txm with command:\n"
echo "$COMMAND"

set +ue
IS_RUNNING=`screen -ls | grep Txm4txm`
if [ -z "$IS_RUNNING" ]
then
    set -ue
    echo "txm4txm service currently not running, starting..."
    screen -S Txm4txm -dm bash -c "$COMMAND"
else
    set -ue
    echo "txm4txm already running, restarting..."
    screen -S Txm4txm -X quit
    screen -S Txm4txm -dm bash -c "$COMMAND"
fi

cd -
