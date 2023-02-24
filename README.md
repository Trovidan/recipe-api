# recipe-api

- Running flake
    ```
        docker-compose run --rm app sh -c "flake8"
    ```

- Create django project
    ```
        docker-compose run --rm app sh -c "django-admin startproject app ."
    ```

- Migrate the db
    ```
        docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"
    ```