Repository for event management system

Initial Setup:

1. Setup postgres database. Default db name is event_management. Default username and password are postgres.
Command on linux to start postgres : sudo -u postgres psql

2. Create a new virtual environment and activate it with following commands in order:
    virtualenv env
    source env/bin/activate

3. Install the required packages by moving into the event_mgmt directory
    cd event_mgmt
    pip install -r requirements.txt

4. Run the following commands to initialize the database
    python manage.py makemigrations
    python manage.py migrate

5. Create a super user/admin with following command (this is the only way for an admin user to exist as of now)
    python manage.py createsuperuser

6. To run the test cases use the following command:
    python manage.py test

    This command will show a test coverage report on command line by default.
    If a html output is desired please execute the following command

    coverage html

7. Run the following command to start server:
    python manage.py runserver

API list:

Can be found in enclosed postman collection
File for postman collection: Event Management.postman_collection.json

Some specific cases:

/auth/logout/ 
/auth/logoutall/ 

For these two apis insert the refresh token obtained in response of login api in Authorization Token part (in postman)

For rest of the apis except /auth/register/ use the access token for authentication in Authorization Token part (in postman)

TO view expanded form of events do the following

/event/1/?expand=image&expand=category => this would lead to expansion of the images array and of category


