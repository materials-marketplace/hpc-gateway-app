import os

from hpc_gateway.factory import create_app

if __name__ == "__main__":
    app = create_app()

    if os.environ.get("DEPLOYMENT", "MC") == "IWM":
        app.config.from_object("hpc_gateway.config.StagingIWMConfig")
        app.run(host="0.0.0.0")
    else:
        # for local MC test
        app.config.from_object("hpc_gateway.config.StagingMCConfig")
        app.run()
else:
    # for dokku deploy in MC
    gunicorn_app = create_app()
    gunicorn_app.config.from_object("hpc_gateway.config.StagingMCConfig")
