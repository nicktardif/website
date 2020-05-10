# Nicktardif.com

### Dependencies
```
pip install pipenv
pipenv install # Update the Python packages
```

### Running
```
./run.sh
```

The API will be available at `localhost:8000/api/v1/`, and the Swagger docs will be available at `localhost:8000/apidocs`

You can use [Postman](https://www.getpostman.com/) as an easy way to test out the API

### Run Tests
```
./launch_tests.sh
```

### Notes

#### How to run Flask Migrate
```
# Initialize Flask Migrate (only needed if your database doesn't exist yet)
pipenv run /bin/bash -c 'FLASK_APP=sec_app flask db init'

# Modify the Python database models, then trigger a migration
pipenv run /bin/bash -c 'FLASK_APP=sec_app/ flask db migrate'

# Upgrade the database with the migration
pipenv run /bin/bash -c 'FLASK_APP=sec_app/ flask db upgrade'
```
