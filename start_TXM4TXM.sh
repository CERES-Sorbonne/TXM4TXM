#!/bin/bash

export TXM_PATH=https://ceres.huma-num.fr/txm4txm
export TXM_PREFIX=/txm4txm
export TXM_PORT=1818
export ROOT_PATH=$TXM_PREFIX
export FOLDER=/home/marceau/GH/TXM4TXM

cd $FOLDER || exit

git pull
source ./venv/bin/activate
pip install -r requirements.txt --quiet

IS_RUNNING=$(ps -aux | grep uvicorn | grep txm4txm)

if [ -z "$IS_RUNNING" ]
then
    echo "europarser service currently not running, starting gunicorn..."
     python -m uvicorn api.api:app --port $TXM_PORT --root-path $ROOT_PATH --workers 8 --limit-max-requests 8 --reload-dir /home/marceau/GH/TXM4TXM --timeout-keep-alive 180
else
    echo "europarser already running, restarting..."
    ps -aux | grep uvicorn | grep txm4txm | awk '{print $2}' | xargs kill -9
    python -m uvicorn api.api:app --port $TXM_PORT --root-path $ROOT_PATH --workers 8 --limit-max-requests 8 --reload-dir /home/marceau/GH/TXM4TXM --timeout-keep-alive 180
fi

cd -



