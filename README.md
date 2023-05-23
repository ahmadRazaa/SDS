# Shared Document Store (SDS)

### installation
tested with Python 3.9+
- Install Python3 and pip3, and create a venv
- Install the dependencies `pip install -r requirements.txt`
- Migrate DB and run server  `python manage.py migrate`, `python manage.py runserver`
- Run test cases with `python manage.py test`
- Create user for auth with `python manage.py createsuperuser`
### API Endpoints

viewset routers
- `http://127.0.0.1:8080/sds/topics/`
- `http://127.0.0.1:8080/sds/folders/`
- `http://127.0.0.1:8080/sds/documents/<?topic="topic_filter">`