FROM python:3.8-slim
RUN pip install pandas
COPY iris.csv /iris.csv
COPY process_iris.py /process_iris.py
ENTRYPOINT ["python", "/process_iris.py"]