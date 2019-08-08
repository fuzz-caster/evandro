import os
import json
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask import redirect
from flask import url_for
import pandas as pd
from environs import Env

from evandro.config import APP_SECRET
from evandro.core.mamdani import predict

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True, static_url_path="")
    app.config.from_mapping(
        SECRET_KEY=APP_SECRET
    )

    try:
        # Ensure instance path exists
        os.makedirs(app.instance_path)
    except OSError:
        # So it already exists... do nothing
        pass

    # Applying cors
    CORS(app)

    # # Register db session hook, and db seed command
    from evandro.db import init_app
    init_app(app)

    from evandro.routes.api import api_blueprint
    app.register_blueprint(api_blueprint)

    @app.route('/')
    def root():
        return app.send_static_file('index.html')

    @app.route('/test')
    def index():
        Xs = pd.read_csv("evandro_data.csv")
        rules = pd.read_csv("rules.csv")
        rules = rules.to_numpy().tolist()
        Xs = Xs.to_numpy()
        x_test = [11300, 7000, 4300]
        result = predict(x_test, Xs, rules)
        return jsonify(result)

    return app