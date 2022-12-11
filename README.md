# MarketPlace HPC Gateway app

## Interact with HPC through MarketPlace proxy using HPC gateway SDK

The HPC gateway SDK is provide for the app developers or the MarketPlace user to run the time consuming tasks over the clusters.

For details of how to use sdk to interact with HPC cluster deployed, read the section [here](../jupyter/hpc-sdk.ipynb)

The following capabilities are supported and can be called by using the SDK.

- Check the availability of system: `app.heartbeat()`
- Create a new user: `app.create_user()`. Only when user first time use the functionality.
- Create a new calculation: `app.create_job()`, the jobid will returned for further job preparation.
- Show job state (List files in job folder): `app.check_job_state(jobid=<jobid>)`, list files in remote job folder.
- Upload file: `app.upload_file(jobid=<jobid>, filename=<filename>, source_path=<local_file_path>`, upload file to remote folder from local path.
- Download file: `app.download_file(jobid=<jobid>, filename=<filename>`, download file from remote folder.
- Delete file: `app.delete_file(jobid=jobid, filename=<filename>)`, delete the file from remote folder.
- Launch job: `app.launch_job(jobid=<jobid>)`, launch/submit the job to cluster queue managed by slurm.
- Cancel the job: `app.cancel_job(jobid=jobid)`, cancel the job submitted.

## Development for a new cluster (For HPC resource providers)

If you have HPC resource provided, you can use our template repository to deploy the App and host it for other MarketPlace users or App developers.

The repository is https://github.com/materials-marketplace/hpc-gateway-app, we use it to deploy our two demo server, the EPFL Materials Cloud (mc) server and the IWM server which the cluster is behind the firewall and using broker to comunicate through proxy.

- Create a virtual environment, activate it and install the dependencies.
- `pip install -e ".[deploy]"`
- Run `python run.py` to start the development server.
- Navigate to http://localhost:5005/. The app will automatically reload if you change any of the source files.

Also check the [`deploy` folder](https://github.com/materials-marketplace/hpc-gateway-app/tree/main/deploy) for how to deploy the self-hosted mongodb database to store the users and jobs information, and how the broker is hosted to relay the requests to the app across the firewall.

## Registry the app to MarketPlace

The you need register the app to MarketPlace, the example openAPI configure files are [openAPI-CSCS-v2.yml](https://github.com/materials-marketplace/hpc-gateway-app/blob/main/openAPI-CSCS-v2.yml), adn [openAPI-IWM-v2.yml](https://github.com/materials-marketplace/hpc-gateway-app/blob/main/openAPI-IWM-v2.yml).

https://materials-marketplace.readthedocs.io/en/latest/apps/registration.html

## Details of deploying the infracstructures and run hpc-gateway app on IWM HPC cluster

Go to the `hpc-gateway-app/deploy` folder and create a `.env` file from `env.template` and fill the field with deployment parameters.
The `F7T_TOKEN` is the public key correspond to the private key of the pair store in the firecrest deployment.
Start the services by running: `docker-compose up -d`.

### Firecrest deployment

The firecrest on MarketPlace firecrest server need to be started.
Go to `firecrest/` folder of `hpc-fire` server and run `docker-compose up -d`.
The changes of firecrest deployment that needed on MarketPlace HPC can be found on https://github.com/unkcpz/firecrest/pull/1

### HPC gateway app and rpc-broker service

[.deploy/docker-compose.yml]
Then need to start the hpc-gateway-app to communicate to the firecrest.
Since the hpc-app is in the private internal network, we use MarketPlace broker to talk to public network.
This will start the hpc-app and the `rpc-brocker` (should be optinonal for the hpc-app accessable deployed on public network).

## For maintainers

The release is for SDK but not the deployment.
For the deployment, always clone the repository and using the docker-compose to deploy to the system.

To create a new SDK release, clone the repository, install development dependencies with `pip install '.[dev]'`, and then execute `bumpver update`.
This will:

  1. Create a tagged release with bumped version and push it to the repository.
  2. Trigger a GitHub actions workflow that creates a GitHub release.

Additional notes:

  - Use the `--dry` option to preview the release change.
  - The release tag (e.g. a/b/rc) is determined from the last release.
    Use the `--tag` option to switch the release tag.

## MIT License

Copyright (c) 2021 Jusong Yu (EPFL)

All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgements

This work is supported by the
[MARVEL National Centre for Competency in Research](<http://nccr-marvel.ch>) funded by the [Swiss National Science Foundation](<http://www.snf.ch/en>),
and the MarketPlace project funded by [Horizon 2020](https://ec.europa.eu/programmes/horizon2020/) under the H2020-NMBP-25-2017 call (Grant No. 760173).

<div style="text-align:center">
 <img src="miscellaneous/logos/MARVEL.png" alt="MARVEL" height="75px">
 <img src="miscellaneous/logos/MarketPlace.png" alt="MarketPlace" height="75px">
</div>
