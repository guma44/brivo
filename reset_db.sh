rm -rf data/brivo.db 
rm -rf brivo/users/migrations/*
rm -rf brivo/brew/migrations/*
sudo docker-compose -f local.yml run --rm django python manage.py makemigrations
sudo docker-compose -f local.yml run --rm django python manage.py makemigrations brew
sudo docker-compose -f local.yml run --rm django python manage.py makemigrations users
sudo docker-compose -f local.yml run --rm django python manage.py migrate
sudo docker-compose -f local.yml run --rm django python manage.py load_db_data
