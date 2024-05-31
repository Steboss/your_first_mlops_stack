import kfp
from kfp import dsl


@dsl.container_component
def iris_processing_op():
    return dsl.ContainerSpec(
        image='sbsynth/iris-processor:latest',
        command=["python", "/process_iris.py"],
        args=[
            "--input-csv", "/iris.csv",
        ]
    )


@dsl.pipeline(
   name='Iris Processing Pipeline',
   description='An example pipeline that processes the Iris dataset.'
)
def iris_pipeline():
    iris_output = iris_processing_op()
    iris_output.set_caching_options(False)


# Compile the pipeline
kfp.compiler.Compiler().compile(iris_pipeline, 'iris_pipeline.yaml')
