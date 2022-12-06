from hpc_gateway.model.job import create_job_script


def test_create_cscs_job_script():
    got = create_job_script(
        job_name="job00",
        image="docker://alpine:latest",
        email="a@b.c",
        partition="debug",
        ntasks_per_node=2,
        executable_cmd="bash -n executable < in > out",
    )

    assert "docker://alpine:latest" in got
