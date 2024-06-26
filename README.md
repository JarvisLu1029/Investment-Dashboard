# Investment-Dashboard screenshot
![image](https://github.com/JarvisLu1029/Investment-Dashboard/assets/115854341/2876619f-79e5-4796-bc0b-07de4b5320bb)

# Run it using Docker Compose
Start docker containers. This can take a few minutes the first time because the backend image needs to download chrome and install all python package.
```
docker compose up
```
When the containers are running, Create all table using Django command in dashboard_backend container.
```
docker compose exec dashboard_backend bash -c "python manage.py migrate"
```

### Using demo data
If you want to use demo data, you can load data in fixtures, run:
```
docker compose exec dashboard_backend bash -c "python manage.py loaddata fixtures/*"
```
Then run:
```
docker compose exec dashboard_backend bash -c "python manage.py runserver 0.0.0.0:80"
```
You will see the web at `localhost:8080/jarvis`
