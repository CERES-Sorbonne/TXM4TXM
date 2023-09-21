#!/bin/bash



cd $FOLDER

git pull
source ./venv/bin/activate
pip install -r requirements.txt --quiet

IS_RUNNING=$(ps -aux | grep uvicorn | grep txm4txm)

if [ -z "$IS_RUNNING"]
then
    echo "europarser service currently not running, starting gunicorn..."
     python -m uvicorn api.api:app --port $TXM_PORT --root-path /txm4txm --workers 8 --limit-max-requests 8 --reload-dir /home/marceau/GH/TXM4TXM --timeout-keep-alive 180
else
    echo "europarser already running, restarting..."
    ps -aux | grep uvicorn | grep txm4txm | awk '{print $2}' | xargs kill -9
fi
cd -



