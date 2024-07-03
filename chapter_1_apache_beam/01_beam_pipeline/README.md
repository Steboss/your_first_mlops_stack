### A simple pipeline in Apache Beam

This is the first example of a Beam pipeline.

#### 1. Install a conda environment or the Beam requirements

To start you can install a conda environment on your laptop through the script `scripts/create_conda_env.sh`.
This script wil install conda as well as the needed python requirements for running the Beam pipeline:

```bash
bash scripts/create_conda_env.sh

# activate the conda environment
conda activate beam_pipeline
```

If you do not want to have `conda` on your laptop, you can install everything in a virtual environment:
```bash
python -m venv venv

# activate your virtual environment
venv/bin/activate
# install the requirements
pip install -r requirements.txt
```

#### 2. Run the pipeline

To run the pipeline locally is very simple, you just need to run the python code:

```bash
python wordcount.py
```