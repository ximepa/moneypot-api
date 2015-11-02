#!/bin/bash
set -e
NUM_WORKERS=3
ADDRESS=0.0.0.0:8083
exec gunicorn moneypot.wsgi:application -w $NUM_WORKERS --bind=$ADDRESS --log-level=info
