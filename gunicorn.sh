#!/bin/bash
set -e
LOGFILE=/var/log/gunicorn/moneypot-api.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=3
# user/group to run as
USER=maxim
GROUP=maxim
ADDRESS=127.0.0.1:8003
cd /home/maxim/production/moneypot-api
source env/bin/activate
test -d $LOGDIR || mkdir -p $LOGDIR
exec gunicorn moneypot.wsgi:application -w $NUM_WORKERS --bind=$ADDRESS \
  --user=$USER --group=$GROUP --log-level=debug \
  --log-file=$LOGFILE 2>>$LOGFILE
