FROM python:3.7.3-alpine

WORKDIR /opt/app

# Install the requirements
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy the code
COPY ./tiny ./tiny
COPY ./config.py ./config.py
COPY ./run.py ./run.py

# Run the app
CMD gunicorn --bind=0.0.0.0:8000 --workers=4 --reload run:app
