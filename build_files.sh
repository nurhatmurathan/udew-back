# build_files.sh
python manage.py makemigrations 
python manage.py migrate
pip install -r requirements.txt
python3.9 manage.py collectstatic
