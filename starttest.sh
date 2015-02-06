#!/bin/bash

set -e

LOGFILE=/srv/domain/logs/domain.log

ERRORFILE=/srv/domain/logs/error.log

LOGDIR=$(dirname $LOGFILE)

NUM_WORKERS=3

#The below address:port info will be used later to configure Nginx with Gunicorn

ADDRESS=127.0.0.1:8003

# user/group to run as

#USER=your_unix_user

#GROUP=your_unix_group

cd /srv/domain

test -d $LOGDIR || mkdir -p $LOGDIR

exec gunicorn_django -w $NUM_WORKERS --bind=$ADDRESS --reload=True \

--log-level=debug \

--log-file=$LOGFILE 2>>$LOGFILE  1>>$ERRORFILE  &