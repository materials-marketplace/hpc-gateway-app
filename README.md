# Authentication with Flask and JWT

## Development server

- Create a virtual environment, activate it and install the dependencies.
- Run `flask run` to start the development server.
- Navigate to http://localhost:5005/. The app will automatically reload if you change any of the source files.

## Interacte with HPC through MarketPlace proxy

For demo jupyter notebook and the SDK of using this app please check [hpc-sdk](https://github.com/unkcpz/hpc-sdk)

## How to deploy the infracstructures and run hpc-app on MarketPlace platform for MarketPlace HPC.

The firecrest on MarketPlace firecrest server need to be started. 
Go to `firecrest/` folder of `hpc-fire` server and run `docker-compose up -d`. 
The changes of firecrest deployment that needed on MarketPlace HPC can be found on https://github.com/unkcpz/firecrest/pull/1

Then need to start the hpc-app to communicate to the firecrest. 
Since the hpc-app is in the private internal network, we use MarketPlace broker to talk to public network.
Go to the hpc-app repo and run `python app.py` (WIP: using docker-compose to start so the dependencies are not needed).
This will start the hpc-app and the `rpc-brocker` (should be optinonal for the hpc-app accessable deployed on public network). 

© 2021 GitHub, Inc.