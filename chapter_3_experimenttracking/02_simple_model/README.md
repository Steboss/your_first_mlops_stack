### An MLFlow pipeline locally

This is a simple example, using a random forest model with MLflow, to be run locally. As per KFP we will use two shells


#### 1. Start up the MLflow UI

In the current shell you're working on, spin up the mlflow ui. Within your conda environment or `venv` just run:
```
mlflow ui
```

Then go to your favourite browser and head to `http://localhost:5000`. You'll see the MLflow UI


#### 2. Run the MLflow code

It's now time to run our experiment tracking:
```bash
python main.py
```
The script will run and MLflow will start recording all its info.
You can see in the MLflow UI the final info registered.