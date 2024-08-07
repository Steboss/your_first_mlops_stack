### Example on Dataflow flex template deployment

This is an example on using Beam Windowing, deploying the pipeline with the flex template.

#### 1. Setup the Dataflow environment in GCP shell

Follow the slides to setup the GCP environment. Then, activate the GCP Shell in your GCP project.


#### 2. Clone the repo

From the bash shell, clone this repository:

```bash
git clone https://github.com/Steboss/your_first_mlops_stack.git
```
Then `cd` in the repository folder and install the requirements:
```bash
cd your_first_mlops_stack/sawtooth_window
```

#### 3. Build the docker image and flex template

The first step for creating a Dataflow flex template is to build the image of the pipeline. Then, this image can be used to create a flex template for dataflow.
The script `scripts/build_flex_template.sh` does this for you. Run it as:
```bash
bash scripts/build_flex_template.sh
```

#### 4. Deploy the flex template

It's now time to deploy the flex template and see it working! The script `scripts/run_flex_template.sh` does this for you. Run it as:
```bash
bash scripts/run_flex_template.sh
```

The script invokes `gcloud dataflow flex-template run`, and it sets up the input conditions and parameters we want to use. In this case, the pipeline will run on a `n1-standard-2` machine with 1 worker.


#### 5. How the sawtooth window works
