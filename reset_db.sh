rm -rf data/brivo.db 
rm -rf brivo/users/migrations/0*
rm -rf brivo/brew/migrations/0*
sudo docker-compose -f local.yml run --rm django python manage.py makemigrations
sudo docker-compose -f local.yml run --rm django python manage.py migrate
sudo docker-compose -f local.yml run --rm django python manage.py load_db_data
