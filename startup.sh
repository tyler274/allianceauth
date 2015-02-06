#!/usr/bin/env bash


# TODO route log output to file.
yes yes | python manage.py collectstatic
python manage.py syncdb

#python manage.py shell < run_alliance_corp_update.py

#python manage.py celeryd &
#python manage.py celerybeat &
screen -dm bash -c 'python manage.py celeryd --verbosity=2 --loglevel=DEBUG'
screen -dm bash -c 'python manage.py celerybeat --verbosity=2 --loglevel=DEBUG'

screen -dm bash -c 'gunicorn_django --workers=5 --bind 127.0.0.1:8000'

#python manage.py runserver &
#gunicorn_django --workers=5 --bind 127.0.0.1:8000 &
