screen -S $screenname testbovril
python manage.py celeryd &
python manage.py celerybeat &
screen -d
