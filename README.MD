# Getting started

### Build & Startup
`docker-compose up -d --build`

### Static file collection (important to remember to do this if you change static files)
`docker-compose exec django_wsgi python3 manage.py collectstatic --no-input`

### Migrate site
`docker-compose exec django_wsgi python3 manage.py migrate`

### Load the initial data for testing/login
`docker-compose exec django_wsgi python3 manage.py loaddata testing_data`

### Done!
Login as 'test_admin' with password 'test_admin'


## Triggering UI events

Note: At the moment I can't seem to get Websockets working - there is some bug I have to look into
So for now things are triggered manually

### 'Toast' Notifications

Enter into a Debugger Console in browser and enter:

`display_notification({"text": "testing notification", "style": "danger"})`

The code governing this is in line:185 of ui_base.html. Try out different style values and feel free to modify.

### Map data flows

TBD

### Access requests etc

Use the Administrator view to modify access-item/access-group request states
You can also modify workorders but it doesn't trigger anything in the UI at this stage (websocket broken)
