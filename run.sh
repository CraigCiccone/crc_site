#!/bin/sh
flask db upgrade
uwsgi --http :5000 --manage-script-name --mount /=run:app --master --processes 4 --threads 2
