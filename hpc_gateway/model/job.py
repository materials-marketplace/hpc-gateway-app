"""Job scripts and singularity
"""
from jinja2 import Environment, FileSystemLoader

environment = Environment(loader=FileSystemLoader("templates/"))


def create_job_script(
    job_name, image, email, partition, ntasks_per_node, executable_cmd
) -> str:
    """The content of the job script"""
    template = environment.get_template("cscs_job_script.j2")

    content = template.render(
        job_name=job_name,
        email=email,
        ntasks_per_node=ntasks_per_node,
        partition=partition,
        image=image,
        executable_cmd=executable_cmd,
    )

    return content
