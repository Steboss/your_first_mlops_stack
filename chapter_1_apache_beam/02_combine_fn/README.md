### Example on `CombineFn`

This example shows how to use the Transform `CombineFn`. To work with this code, it is necessary to create an initial log files with `generate_data.py` script.

#### 1. Install a conda environment or the Beam requirements

To start you can install a conda environment on your laptop through the script `scripts/create_conda_env.sh`.
This script wil install conda as well as the needed python requirements for running the Beam pipeline:

```bash
bash scripts/create_conda_env.sh

# activate the conda environment
conda activate combine_pipeline
```

If you do not want to have `conda` on your laptop, you can install everything in a virtual environment:
```bash
python -m venv venv

# activate your virtual environment
venv/bin/activate
# install the requirements
pip install -r requirements.txt
```

#### 2. Generate the input data

The input data we are going to work on are generated with `generated_data.py`. A file called `log_entries_large.txt` will be created:

```bash
python generate_data.py 100
```
The command above will generate a file with 100 rows. If you want to try Beam on chunkier files, you just need to increase the value, e.g. 1000, 10000. Be aware, a value > 10M may take some time to be generated - as well as some space on your local disk

#### 3. Run the pipeline

Run the combine pipeline

```bash
DATE=$(date + %Y%m%d)
python combine --input-file -log_entries_large.txt --output-file output-word-count-${DATE}.txt
```

This command will run the Beam pipeline locally. An output file called `output-word-count-*.txt` will be generated. The file will have a suffix that is given by today's date.