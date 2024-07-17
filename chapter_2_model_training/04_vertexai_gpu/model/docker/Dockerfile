FROM tensorflow/tensorflow:2.10.0-gpu

ARG WORKDIR=/mlflow_tutorial
RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}

RUN python -m pip install matplotlib
RUN python -m pip install scikit-learn numpy
COPY model_gpu.py ${WORKDIR}/model.py

CMD ["python", "model.py"]
