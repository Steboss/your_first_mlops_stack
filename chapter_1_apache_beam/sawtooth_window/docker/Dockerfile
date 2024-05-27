FROM gcr.io/dataflow-templates-base/python39-template-launcher-base

ARG WORKDIR=/template
RUN mkdir -p $WORKDIR
WORKDIR ${WORKDIR}

ENV PYTHONPATH ${WORKDIR}
COPY pipeline pipeline
COPY requirements.txt requirements.txt
COPY setup.py setup.py

RUN apt-get update \
    && apt-get install -y libffi-dev git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install apache-beam[gcp] \
    && pip install -r requirements.txt \
    # Download the requirements to speed up launching the Dataflow job.
    && pip download --no-cache-dir --dest /tmp/dataflow-requirements-cache -r requirements.txt \
    && pip download --no-cache-dir --dest /tmp/dataflow-requirements-cache .


ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${WORKDIR}/requirements.txt"
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/pipeline/processing_logs.py"
ENV FLEX_TEMPLATE_PYTHON_SETUP_FILE="${WORKDIR}/setup.py"

ENV PIP_NO_DEPS=True
ENTRYPOINT [ "/opt/apache/beam/boot" ]