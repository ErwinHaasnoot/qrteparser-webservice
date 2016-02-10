Welcome to the QRTEParser Django webservice project!

Parser v2


## Introduction

This project is intended as a replacement for the QRTEParser written in Java. If you've found your way to this repository,
you're most likely interested in hosting using the local python parser, or hosting your own webserver. However, for completeness sake, the webservice
we offer can be found here:

    https://parser.qrtengine.com/

## Warning

Currently, the parser has only been tested for Python2.7. It will not work for Python3 You can check which version of Python you're running by doing

    $ python -V

Generally, both python3 and python2 are installed on pc's. If your python is linked to python3, you can check whether any of the following work:

    python2 -V
    python27 -V

## Installing Python

Please look here for a guide on how to install python for your OS:

    https://www.python.org/about/gettingstarted/


## Quick Usage

In case you want to run the parser without the webservice overhead, you can simply use parser.py found in the project's
root directory

    $ python parser.py path/to/file.csv


## Starting from the Terminal

In case you want to run your Django application from the terminal just run:

1) Rename settings.sample.py to settings.py in qparser

    $ mv qparser/settings.sample.py qparser/settings.py

2) Install requirements using PIP

     $ sudo pip install -r requirements.txt

3) Create your database migrations

    $ python manage.py makemigrations
    
4) Build your database

    $ python manage.py migrate

5) Run your webserver

    $ python manage.py runserver
    
    
## Support & Documentation

QRTEngine website can be found at:
    www.qrtengine.com
