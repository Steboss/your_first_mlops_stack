### A simple pipeline in Apache Beam

This is the first example of a Beam pipeline.
To start you can install a conda environment on your laptop through the script `scripts/create_conda_env.sh`.
This script wil install conda as well as the needed python requirements for running the Beam pipeline:

```bash
bash scripts/create_conda_env.sh
```

To run the pipeline you'll need to activate the conda environment (if not already). To activate the environment:
```bash
conda activate beam_pipeline
```

And then, to run the pipeline:
```bash
python wordcount.py
```