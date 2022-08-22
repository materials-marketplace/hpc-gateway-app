# MarketPlace HPC Gateway app

## Development and run locally

- Create a virtual environment, activate it and install the dependencies.
- `pip install -U ".[dev]"`
- Run `python app.py` to start the development server.
- Navigate to http://localhost:5005/. The app will automatically reload if you change any of the source files.

## Registry the app to MarketPlace

https://materials-marketplace.readthedocs.io/en/latest/apps/registration.html

## Interacte with HPC through MarketPlace proxy

Check [materials-marketplace-hpc-sdk]() for how to use the app to communicate with HPC cluster.

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
Then need to start the hpc-app to communicate to the firecrest. 
Since the hpc-app is in the private internal network, we use MarketPlace broker to talk to public network.
Go to the hpc-app repo and run `python app.py` (WIP: using docker-compose to start so the dependencies are not needed).
This will start the hpc-app and the `rpc-brocker` (should be optinonal for the hpc-app accessable deployed on public network). 

