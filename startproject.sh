#!/bin/sh
cd /workspace/app
python ./module/table_init.py
python ./module/MOTCdata_init.py
uwsgi --ini app.ini
#python -m flask run --host=0.0.0.0 --port=3000