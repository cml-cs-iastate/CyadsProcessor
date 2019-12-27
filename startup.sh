#!/bin/bash

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn CyadsProcessor.wsgi:application \
    --bind 0.0.0.0:8000 \
    --reload \
    --workers 8 \
    --timeout 3600 \
    --graceful-timeout 3600
