### An MLFlow pipeline locally

This is a simple example, using a random forest model with MLflow, to be run locally. As per KFP we will use two shells

#### 1. Installation of MLflow locally

As always, you can install MLflow throuhg `conda` or `venv`
To start you can install a conda environment on your laptop through the script `scripts/create_conda_env.sh`.

```bash
bash scripts/create_conda_env.sh

# activate the conda environment
conda activate mlflow_local
```

If you do not want to have `conda` on your laptop, you can install everything in a virtual environment:
```bash
python -m venv venv

# activate your virtual environment
venv/bin/activate
# install the requirements
pip install -r requirements.txt
```

#### 2. Start up the MLflow UI

In the current shell you're working on, spin up the mlflow ui. Within your conda environment or `venv` just run:
```
mlflow ui
```

Then go to your favourite browser and head to `http://localhost:5000`. You'll see the MLflow UI


#### 3. Run the MLflow code

It's now time to run our experiment tracking:
```bash
python main.py
```
The script will run and MLflow will start recording all its info.
You can see in the MLflow UI the final info registered.