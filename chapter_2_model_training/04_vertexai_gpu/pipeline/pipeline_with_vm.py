import kfp
from kfp.v2 import compiler
from kfp.v2.dsl import component
from google.cloud.aiplatform import pipeline_jobs
from typing import Optional
import json


@component(
    base_image="google/cloud-sdk:latest",
    packages_to_install=["google-cloud-compute==1.6.1"],
)
def train_on_gpu(
    project_id: str,
    instance_name: str,
    location: str,
    model_image: str,
    artefacts_bucket: str,
    machine_type: str = "n1-standard-1",
    accelerator: str = "nvidia-tesla-t4",
    accelerator_count: int = 1,
    machine_image_family: str = "pytorch-latest-gpu",
    boot_disk_size: int = 50,
    startup_script: Optional[str] = None,
    after_component: Optional[str] = None,
) -> str:
    r"""This component sets up a GPU machine. The training will start as soon as the machine has been
    configured.

    Parameters
    -----------
    project_id: str, project id
    instance_name: str, name of the machine
    location: str, region
    model_image: str, image of the model to run
    artefacts_bucket: str, the bucket where artefacts will be saved
    machine_type: str, machine type for the VM
    accelerator: str, the GPU type you want to use, default nvidia-tesla-t4
    accelerator_count: int, the number of GPUs needed
    machine_image_family: str, VM images to set up the machine (e.g. CUDA installation).
                        Check https://cloud.google.com/deep-learning-vm/docs/images#images to select the right family for your app
    boot_disk_size: int, the size of the VM disk.
    startup_script: str, VM startup script. This is a GCS path to a custom startup script. If not given, startup will be generated
    after_compoment: str, dummy compoment to allow chaining

    Return
    ------
    instance.id: str, the id of the created instance
    """
    import re
    import sys
    import os
    import warnings
    from typing import Any, List

    from google.api_core.extended_operation import ExtendedOperation
    from google.cloud import compute_v1
    import logging

    logging.getLogger().setLevel(logging.INFO)

    def get_image_from_family(project: str, family: str) -> compute_v1.Image:
        """
        Retrieve the newest image that is part of a given family in a project.
        Args:
            project: project ID or project number of the Cloud project you want to get image from.
            family: name of the image family you want to get image from.
        Returns:
            An Image object.
        """
        image_client = compute_v1.ImagesClient()
        # List of public operating system (OS) images: https://cloud.google.com/compute/docs/images/os-details
        newest_image = image_client.get_from_family(project=project, family=family)
        return newest_image

    def disk_from_image(
        disk_type: str,
        disk_size_gb: int,
        boot: bool,
        source_image: str,
        auto_delete: bool = True,
    ) -> compute_v1.AttachedDisk:
        """
        Create an AttachedDisk object to be used in VM instance creation. Uses an image as the
        source for the new disk.
        Args:
             disk_type: the type of disk you want to create. This value uses the following format:
                "zones/{zone}/diskTypes/(pd-standard|pd-ssd|pd-balanced|pd-extreme)".
                For example: "zones/us-west3-b/diskTypes/pd-ssd"
            disk_size_gb: size of the new disk in gigabytes
            boot: boolean flag indicating whether this disk should be used as a boot disk of an instance
            source_image: source image to use when creating this disk. You must have read access to this disk. This can be one
                of the publicly available images or an image from one of your projects.
                This value uses the following format: "projects/{project_name}/global/images/{image_name}"
            auto_delete: boolean flag indicating whether this disk should be deleted with the VM that uses it
        Returns:
            AttachedDisk object configured to be created using the specified image.
        """
        boot_disk = compute_v1.AttachedDisk()
        initialize_params = compute_v1.AttachedDiskInitializeParams()
        initialize_params.source_image = source_image
        initialize_params.disk_size_gb = disk_size_gb
        initialize_params.disk_type = disk_type
        boot_disk.initialize_params = initialize_params
        # Remember to set auto_delete to True if you want the disk to be deleted when you delete
        # your VM instance.
        boot_disk.auto_delete = auto_delete
        boot_disk.boot = boot
        return boot_disk

    def create_instance(
        project_id: str,
        project_number: str,
        startup_script: str,
        zone: str,
        instance_name: str,
        disks: List[compute_v1.AttachedDisk],
        machine_type: str = "n1-standard-1",
        network_link: str = "global/networks/default",
        external_access: bool = False,
        external_ipv4: str = None,
        accelerators: List[compute_v1.AcceleratorConfig] = None,
        preemptible: bool = False,
        custom_hostname: str = None,
    ) -> compute_v1.Instance:
        """
        Send an instance creation request to the Compute Engine API and wait for it to complete.
        Args:
            project_id: project ID or project number of the Cloud project you want to use.
            zone: name of the zone to create the instance in. For example: "us-west3-b"
            instance_name: name of the new virtual machine (VM) instance.
            disks: a list of compute_v1.AttachedDisk objects describing the disks
                you want to attach to your new instance.
            machine_type: machine type of the VM being created. This value uses the
                following format: "zones/{zone}/machineTypes/{type_name}".
                For example: "zones/europe-west3-c/machineTypes/f1-micro"
            network_link: name of the network you want the new instance to use.
                For example: "global/networks/default" represents the network
                named "default", which is created automatically for each project.
            subnetwork_link: name of the subnetwork you want the new instance to use.
                This value uses the following format:
                "regions/{region}/subnetworks/{subnetwork_name}"
            internal_ip: internal IP address you want to assign to the new instance.
                By default, a free address from the pool of available internal IP addresses of
                used subnet will be used.
            external_access: boolean flag indicating if the instance should have an external IPv4
                address assigned.
            external_ipv4: external IPv4 address to be assigned to this instance. If you specify
                an external IP address, it must live in the same region as the zone of the instance.
                This setting requires `external_access` to be set to True to work.
            accelerators: a list of AcceleratorConfig objects describing the accelerators that will
                be attached to the new instance.
            preemptible: boolean value indicating if the new instance should be preemptible
                or not. Preemptible VMs have been deprecated and you should now use Spot VMs.
            spot: boolean value indicating if the new instance should be a Spot VM or not.
            instance_termination_action: What action should be taken once a Spot VM is terminated.
                Possible values: "STOP", "DELETE"
            custom_hostname: Custom hostname of the new VM instance.
                Custom hostnames must conform to RFC 1035 requirements for valid hostnames.
            delete_protection: boolean value indicating if the new virtual machine should be
                protected against deletion or not.
        Returns:
            Instance object.
        """
        instance_client = compute_v1.InstancesClient()

        # Use the network interface provided in the network_link argument.
        #network_interface = compute_v1.NetworkInterface()
        #network_interface.name = network_link

        if external_access:
            access = compute_v1.AccessConfig()
            access.type_ = compute_v1.AccessConfig.Type.ONE_TO_ONE_NAT.name
            access.name = "External NAT"
            access.network_tier = access.NetworkTier.PREMIUM.name
            if external_ipv4:
                access.nat_i_p = external_ipv4
            #network_interface.access_configs = [access]

        # Collect information into the Instance object.
        instance = compute_v1.Instance()
        #instance.network_interfaces = [network_interface]
        instance.name = instance_name

        # Setup metadata
        metadata = compute_v1.Metadata()
        metadata.items = [
            {"key": "startup-script", "value": startup_script},
            {"key": "google-logging-enabled", "value": "true"},
        ]

        instance.metadata = metadata

        # Setup service account and scopes
        sa = compute_v1.ServiceAccount()
        sa.email = f"{project_number}-compute@developer.gserviceaccount.com"
        sa.scopes = [
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/cloud-platform.read-only",
            "https://www.googleapis.com/auth/devstorage.full_control",
            "https://www.googleapis.com/auth/monitoring.write",
        ]
        instance.service_accounts = [sa]

        # setup disks and scheduling
        instance.disks = disks
        instance.scheduling = compute_v1.Scheduling()
        instance.scheduling.on_host_maintenance = (
            "TERMINATE"  # this is a must for GPU instances
        )
        if re.match(r"^zones/[a-z\d\-]+/machineTypes/[a-z\d\-]+$", machine_type):
            instance.machine_type = machine_type
        else:
            instance.machine_type = f"zones/{zone}/machineTypes/{machine_type}"

        if accelerators:
            instance.guest_accelerators = accelerators

        if preemptible:
            # Set the pre-emptible setting
            warnings.warn(
                "Preemptible VMs are being replaced by Spot VMs.", DeprecationWarning
            )

            instance.scheduling.preemptible = True

        if custom_hostname is not None:
            # Set the custom hostname for the instance
            instance.hostname = custom_hostname

        # Prepare the request to insert an instance.
        request = compute_v1.InsertInstanceRequest()
        request.zone = zone
        request.project = project_id
        request.instance_resource = instance

        # Wait for the create operation to complete.
        logging.info(f"Creating the {instance_name} instance in {zone}...")

        operation = instance_client.insert(request=request)

        wait_for_extended_operation(operation, "instance creation")

        logging.info(f"Instance {instance_name} created.")

        return instance_client.get(
            project=project_id, zone=zone, instance=instance_name
        )

    def wait_for_extended_operation(
        operation: ExtendedOperation,
        verbose_name: str = "operation",
        timeout: int = 300,
    ) -> Any:
        """
        This method will wait for the extended (long-running) operation to
        complete. If the operation is successful, it will return its result.
        If the operation ends with an error, an exception will be raised.
        If there were any warnings during the execution of the operation
        they will be printed to sys.stderr.
        Args:
            operation: a long-running operation you want to wait on.
            verbose_name: (optional) a more verbose name of the operation,
                used only during error and warning reporting.
            timeout: how long (in seconds) to wait for operation to finish.
                If None, wait indefinitely.
        Returns:
            Whatever the operation.result() returns.
        Raises:
            This method will raise the exception received from `operation.exception()`
            or RuntimeError if there is no exception set, but there is an `error_code`
            set for the `operation`.
            In case of an operation taking longer than `timeout` seconds to complete,
            a `concurrent.futures.TimeoutError` will be raised.
        """
        result = operation.result(timeout=timeout)

        if operation.error_code:
            print(
                f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}",
                file=sys.stderr,
                flush=True,
            )
            print(f"Operation ID: {operation.name}", file=sys.stderr, flush=True)
            raise operation.exception() or RuntimeError(operation.error_message)

        if operation.warnings:
            print(f"Warnings during {verbose_name}:\n", file=sys.stderr, flush=True)
            for warning in operation.warnings:
                print(
                    f" - {warning.code}: {warning.message}", file=sys.stderr, flush=True
                )

        return result

    project_number = os.environ["CLOUD_ML_PROJECT_ID"]
    logging.info(f"Project {project_number}")

    # setup disk
    newest_debian = get_image_from_family(
        project="deeplearning-platform-release", family=machine_image_family
    )
    disk_type = f"zones/{location}/diskTypes/pd-standard"
    disks = [disk_from_image(disk_type, boot_disk_size, True, newest_debian.self_link)]

    # setup GPU
    gpu = compute_v1.AcceleratorConfig()
    gpu.accelerator_count = accelerator_count
    gpu.accelerator_type = (
        f"projects/{project_id}/zones/{location}/acceleratorTypes/{accelerator}"
    )
    accelerators = [gpu]

    if not startup_script:
        startup_script = f"""
            #!/usr/bin/env bash
            sleep 30

            echo "Installing GPU drivers"
            /opt/deeplearning/install-driver.sh

            echo "Configuring docker"
            gcloud auth configure-docker

            echo "Run docker image with GPUs and env vars"
            docker run --gpus=all --log-driver=gcplogs -e CLOUD_ML_PROJECT_ID={project_number} -e AIP_MODEL_DIR=gs://{artefacts_bucket} {model_image}
            sleep 60
            echo "shutdown now"
            shutdown -h now;
        """

    vm_instance = create_instance(
        project_id,
        project_number,
        startup_script,
        location,
        instance_name,
        disks,
        accelerators=accelerators,
        machine_type=machine_type,
        external_access=True,
    )
    return str(vm_instance.id)


@kfp.dsl.pipeline(name="gpu-example-2", description="Example for running GPU model")
def pipeline(
    vertex_project: str,
    instance_name: str,
    container_image: str,
    location: str,
    artefacts_bucket: str,
    project_region: str,
    vertex_bucket: str,
    cache: bool,
):
    r"""Main KFP pipeline.

    The pipeline retrieves data from BQ and then it launches a RF model

    Args:
    -----
    vertex_project: str, the project id
    instance_name: str, name of the VM
    container_image: str, the image of the model to run
    location: str, the region to run the VM and VertexAi
    artefacts_bucket: str, name of the output bucket
    """
    train_on_gpu(
        project_id=vertex_project,
        instance_name="tester-vm",
        location=location,
        model_image=container_image,
        artefacts_bucket=artefacts_bucket,
        machine_type="n1-standard-2",  # https://cloud.google.com/compute/docs/gpus
        accelerator="nvidia-tesla-t4",
        accelerator_count=1,
    )


if __name__ == "__main__":
    config = {
        "vertex_project": "data-gearbox-421420",
        "instance_name": "mnist-gpu-example",
        "container_image": "europe-west2-docker.pkg.dev/data-gearbox-421420/model-gpu-vertexai/model_gpu", # noqa
        "location": "europe-west2-b",
        "artefacts_bucket": "vertexai_output_gpu_america",
        # required by the vertex pipeline
        "project_region": "europe-west2",
        "vertex_bucket": "gs://vertexai_inputfiles",
        "cache": False,
    }
    package_path = "pipeline.json"
    pipe = compiler.Compiler().compile(pipeline_func=pipeline, package_path=package_path)
    with open(package_path, "r") as ifile:
        pipeline_specs = json.load(ifile)
    display_name = pipeline_specs["pipelineSpec"]["pipelineInfo"]["name"]
    pipeline = pipeline_jobs.PipelineJob(
            display_name,
            package_path,
            pipeline_root=config["vertex_bucket"],
            parameter_values=config,
            enable_caching=bool(config["cache"]),
            project=config["vertex_project"],
            location=config["project_region"],
        )
    pipeline.submit()
