import kfp
from kfp import dsl


@dsl.container_component
def iris_processing_op():
    return dsl.ContainerSpec(
        image='sbsynth/iris-processor:latest',
        command=["python", "/process_iris.py"],
        args=[
            '--input-csv', '/Users/stefano.bosisio/Documents/medium/beam/your_first_mlops_stack/chapter_2_model_training/02_kubeflow_iris_as_op_local/iris.csv',
            '--output-csv', '/Users/stefano.bosisio/Documents/medium/beam/your_first_mlops_stack/chapter_2_model_training/02_kubeflow_iris_as_op_local/iris_means.csv'
        ]
    )


@dsl.pipeline(
   name='Iris Processing Pipeline',
   description='An example pipeline that processes the Iris dataset.'
)
def iris_pipeline():
    iris_processing_op()


# Compile the pipeline
kfp.compiler.Compiler().compile(iris_pipeline, 'iris_pipeline.yaml')
