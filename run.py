from hpc_gateway.factory import create_app

if __name__ == "__main__":
    app = create_app()
    app.config.from_object("config.StagingConfig")

    app.run()
