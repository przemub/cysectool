#!/bin/sh
# A script that runs the visualiser and restarts it on changes.

# Bokeh settings
export BOKEH_MINIFIED="False"

while true; do
  python main.py &
  PID=$!
  inotifywait --recursive -e modify -e close_write -e move -e create -e delete .
  kill $PID
done
