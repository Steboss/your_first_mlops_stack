FROM python:3.9-slim-buster

RUN apt-get update -q && \
    apt-get install -q -y \
    curl \
    zip \
    unzip \
    libgomp1 \
    gunicorn3 \
    postgresql \
    libpq-dev \
    && apt-get clean

# Adding the package path to local
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

COPY requirements.txt requirements.txt
COPY randomforest.py randomforest.py
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "randomforest.py" ]
