import os
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'invman.sqlite'),
    )
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import start
    app.register_blueprint(start.bp)
    
    from . import main
    app.register_blueprint(main.bp)
    
    from . import db
    db.init_app(app)
    
    return app