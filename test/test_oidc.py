"""
Flask app for testing the OpenID Connect extension.
"""
from flask import Flask
from flask_oidc import OpenIDConnect

# @app.route('/')
def index():
    return "too many secrets", 200, {
        'Content-Type': 'text/plain; charset=utf-8'
    }

def create_app(config, oidc_overrides=None):
    app = Flask(__name__)
    app.config.update(config)
    if oidc_overrides is None:
        oidc_overrides = {}
    oidc = OpenIDConnect(app, **oidc_overrides)
    app.route('/')(oidc.check(index))
    return app

if __name__ == '__main__':
    APP = create_app({
        'OIDC_CLIENT_SECRETS': './auth_config_template.json',
        'OIDC_SCOPES': ["https://api.botframework.com/.default"],
        'OIDC_RESOURCE_SERVER_ONLY': True})
    APP.run(host="127.0.0.1", port=8080, debug=True)