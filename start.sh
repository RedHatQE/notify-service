#! /bin/bash
set -e

_pipenv () {
    ($(command -v pipenv) --version >/dev/null 2>&1 && (pipenv "$@"; return $?)) || \
	    echo "Exited with error, make sure pipenv is installed"
}

while [ $# -gt 0 ]
do
    case $1 in
        --dev )
            DEV=true
            ;;
        -h | --help )
            echo "usage: start.sh [-h] [--dev]
            options:
            --dev       Start with --reload app dir.
            "
            exit 0
            ;;
    esac
    shift
done

if [ -f /app/app/main.py ]; then
    DEFAULT_MODULE_NAME=app.main
elif [ -f /app/main.py ]; then
    DEFAULT_MODULE_NAME=main
fi
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

if [ -f /app/gunicorn_conf.py ]; then
    DEFAULT_GUNICORN_CONF=/app/gunicorn_conf.py
elif [ -f /app/app/gunicorn_conf.py ]; then
    DEFAULT_GUNICORN_CONF=/app/app/gunicorn_conf.py
else
    DEFAULT_GUNICORN_CONF=/gunicorn_conf.py
fi
export GUNICORN_CONF=${GUNICORN_CONF:-$DEFAULT_GUNICORN_CONF}
export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}

# If there's a prestart.sh script in the /app directory or other path specified, run it before starting
PRE_START_PATH=${PRE_START_PATH:-/app/prestart.sh}
echo "Checking for script in $PRE_START_PATH"
if [ -f "$PRE_START_PATH" ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else
    echo "There is no script $PRE_START_PATH"
fi

# Start Gunicorn
if [[ $DEV == 'true' ]]; then
    _pipenv run gunicorn --log-level debug --reload -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"
else
    _pipenv run gunicorn -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"
fi
