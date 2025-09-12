#!/usr/bin/env bash
# start.sh
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
