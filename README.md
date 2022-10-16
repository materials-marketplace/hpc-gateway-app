# MarketPlace HPC Gateway app

## Interact with HPC through MarketPlace proxy using SDK

This repository provide SDK for using or integrating the HPC gateway app into other MarketPlace app.

First, create a `hpc` instance with:

python
```
from marketplace_hpc import HpcGatewayApp

hpc = HpcGatewayApp(
    client_id=<app_id>, # This is the HPC gateway app.
    access_token=<your_access_token>,
)
```

The following capabilities are supported and can be called by using the SDK.

- Check the availability of system: `hpc.heartbeat()`
- Create a new calculation: `hpc.new_job()`, the resourceid will returned to list files on remote workdir, upload/downlead/delete files and the launch/delete job.
- Upload file: `hpc.upload_file(resourceid=<resourceid>, source_path=<file_local_path>`.
- Download file: `hpc.download_file(resourceid=<resourceid>, filename=<filename>`.
- Delete file: `hpc.delete_file(resourceid=resourceid, filename=<filename>)`
- List jobs (only CSCS deployment): `hpc.list_jobs()`.
- Launch job: `hpc.run_job(resourceid=<resourceid>)`
- Delete job: `hpc.delete_job(resourceid=resourceid)`

You can find example at https://github.com/materials-marketplace/hpc-sdk/blob/main/hpc_api.ipynb

### Materials Cloud (CSCS) deployment

The correspond HPC-Gateway app is https://www.materials-marketplace.eu/app/hpc-app (ID: `5fd66c68-50e9-474a-b55d-148777ae3efd`) deployed on production server.

Since it deployed using Materials Cloud CSCS resources provided by EPFL, it is only for test purpose and MarketPlace users who what to use it need to contact Jusong Yu @unkpcz (jusong.yu@epfl.ch) to add your MarketPlace account to the whitelist and then register your account by:

```
curl -X POST \
   -H "Authorization:Bearer <put_your_token_here>" \
   'https://mp-hpc.herokuapp.com/user'
```

### IWM deployment

The correspond HPC-Gateway app is [HPC gateway (broker)](https://staging.materials-marketplace.eu/app/hpc-gateway-broker) (ID: `dc67d85e-7945-49fa-bf85-3159a8358f85`) deployed on staging server since RPC broker server needed.


## Development and run locally for testing

- Create a virtual environment, activate it and install the dependencies.
- `pip install -U ".[dev]"`
- Run `python app.py` to start the development server.
- Navigate to http://localhost:5005/. The app will automatically reload if you change any of the source files.

## Registry the app to MarketPlace

https://materials-marketplace.readthedocs.io/en/latest/apps/registration.html

## How to deploy app to heroku (for Materials Cloud deployment)

Set all the ENV variables in heroku dashbooard (https://devcenter.heroku.com/articles/config-vars). Check `cscs.env.template` for all variables needed.

Install the Heroku CLI
Download and install the Heroku CLI.

If you haven't already, log in to your Heroku account and follow the prompts to create a new SSH public key.

```
$ heroku login --interactive
```

Clone the repository
Use Git to clone mp-hpc's source code to your local machine.

```
$ heroku git:clone -a mp-hpc
$ cd mp-hpc
```

or in the repo add heroku remote repo to push

```
$ git remote add heroku https://git.heroku.com/mp-hpc.git
```

Deploy your changes
Make some changes to the code you just cloned and deploy them to Heroku using Git.

```
$ git add .
$ git commit -am "make it better"
$ git push heroku master
```

## How to deploy the infracstructures and run hpc-app on IWM HPC.

### Firecrest deployment
The firecrest on MarketPlace firecrest server need to be started.
Go to `firecrest/` folder of `hpc-fire` server and run `docker-compose up -d`.
The changes of firecrest deployment that needed on MarketPlace HPC can be found on https://github.com/unkcpz/firecrest/pull/1

### HPC-GW app and rpc-broker server
[.deploy/docker-compose.yml]
Then need to start the hpc-gateway-app to communicate to the firecrest.
Since the hpc-app is in the private internal network, we use MarketPlace broker to talk to public network.
Go to the hpc-app repo and run `python app.py` (WIP: using docker-compose to start so the dependencies are not needed).
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
