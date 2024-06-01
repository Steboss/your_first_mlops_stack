FROM python:3.8-slim-buster

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
COPY random_forest.py random_forest.py
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "random_forest.py" ]
