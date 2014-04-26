Statistics Browser
==================

This repository has been forked from the O A.D. project.
The intent is to use this as a base for a statistics collection
system for SuperTuxKart.

Installation
============

Before proceeding, install the following packages using your favorite package
manager:
 * postgresql 9.0+
 * python 3.3+
 * python-virtualenv

From the repository root, run:
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `userreport/settings_local.EXAMPLE.py` to `userreport/settings_local.py`, and
edit the settings inside that file to match your environment.

Make sure you have created a database for yourself.

Run `python manage.py syncdb` to create your database.

To start the Django development server, run `python manage.py runserver`

