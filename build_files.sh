# install dependencies
python3.9 -m pip install -r requirements.txt

# collect static files
python3.9 manage.py collectstatic --noinput
commit 