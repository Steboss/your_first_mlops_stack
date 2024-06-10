# create a virtual environment
python3 -m venv venv
venv/bin/pip install "cython<3.0.0" wheel
venv/bin/pip install "pyyaml==5.4.1" --no-build-isolation
venv/bin/pip install -r requirements.txt

cd pipeline
../venv/bin/python pipeline.py

