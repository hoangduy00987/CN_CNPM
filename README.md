chay cau lenh nay ->  docker-compose up --build

docker-compose run --rm web sh -c "python manage.py createsuperuser"
docker-compose run --rm web sh -c "python manage.py makemigrations"
docker-compose run --rm web sh -c "python manage.py migrate"