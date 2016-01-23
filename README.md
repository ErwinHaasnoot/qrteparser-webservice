Welcome to the QRTEParser Django webservice project!

Parser v2


## Introduction

This project is intended as a replacement for the QRTEParser written in Java. If you've found your way to this repository,
you're most likely interested in hosting using the local python parser, or hosting your own webserver. However, for completeness sake, the webservice
we offer can be found here:
https://example.com

## Warning

Currently, the parser has only been tested for Python2.7. It will not work for Python3 You can check which version of Python you're running by doing

    $ python -V

Generally, both python3 and python2 are installed on pc's. If your python is linked to python3, you can check whether any of the following work:

    python2 -V
    python27 -V

## Installing Python

Please look here for a guide on how to install python for your OS:


## Quick Usage

In case you want to run the parser without the webservice overhead, you can simply use parser.py found in the project's
root directory

    $ python parser.py path/to/file.csv


## Starting from the Terminal

In case you want to run your Django application from the terminal just run:

1) Rename settings.sample.py to settings.py in qparser
    $ mv qparser/settings.sample.py qparser/settings.py

2) Run syncdb command to sync models to database and create Django's default superuser and auth system

    $ python manage.py syncdb

3) Run Django

    $ python manage.py runserver $IP:$PORT
    
## Support & Documentation

Django docs can be found at https://www.djangoproject.com/

You may also want to follow the Django tutorial to create your first application:
https://docs.djangoproject.com/en/1.7/intro/tutorial01/