import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# SQLALCHEMY_DATABASE_URI = "postgresql://your_username:your_password@localhost:5432/your_database_name"
SQLALCHEMY_DATABASE_URI = "postgresql://dennisiluma:joshboy1@localhost:5432/todoapp"
