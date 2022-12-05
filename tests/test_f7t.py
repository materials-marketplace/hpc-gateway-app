from hpc_gateway.model.f7t import create_f7t_client

def test_f7t_default(app):
    """The test need to run with environment variable: F7T_SECRET.
    $ F7T_SECRET=... pytest -v -s tests/test_f7t.py"""
    with app.app_context():
        f7t_client = create_f7t_client()
        all_system = f7t_client.all_systems()
        
        assert all_system[0].get("status") == "available"
        
def test_f7t_list_scratch(app):
    """call files list of scratch"""
    with app.app_context():
        f7t_client = create_f7t_client()
        file_list = f7t_client.list_files(machine='daint', target_path='/scratch')
        
        assert file_list is not None
    
    