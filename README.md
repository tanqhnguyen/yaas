# Folder structure
* `backend` contains the main code for the project
* `provision` contains provision code used for setting up the environment

# Installation Instruction
* Install python (2.7)
* Install pip

# Install dependencies
* pip install -r backend/requirements.txt

# First start the project
1. Setting up the database `python manage.py syncdb`
2. Migrate database schema `python manage.py migrate`
3. Manually create an admin user `python manage.py createsuperuser`

# Start server
* python manage.py runserver

# Start celery worker to do background tasks
* python manage.py celery worker --loglevel=info

# Note about provision
* There are provision code for using with chef-solo. The code is stored inside `provision/chef`
* The provision code is compatible with `vagrant`