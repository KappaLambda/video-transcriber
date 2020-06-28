#!/bin/bash
function abspath() {
    # generate absolute path from relative path
    # $1     : relative filename
    # return : absolute path
    if [ -d "$1" ]; then
        # dir
        (cd "$1"; pwd)
    elif [ -f "$1" ]; then
        # file
        if [[ $1 == */* ]]; then
            echo "$(cd "${1%/*}"; pwd)/${1##*/}"
        else
            echo "$(pwd)/$1"
        fi
    fi
}

export GOOGLE_APPLICATION_CREDENTIALS=$(abspath google-application-credentials.json)
$(pyenv which gunicorn) \
    --reload \
    --timeout 300 \
    --chdir ./video_transcriber/ \
    --access-logfile - \
    --workers 3 \
    --bind unix:/tmp/video_transcriber.sock \
    video_transcriber.wsgi:application
