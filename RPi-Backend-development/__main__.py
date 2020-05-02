import logging
import tornado
import tornado.ioloop
from tornado.options import options
from ssh import handler
from ssh.handler import IndexHandler, WsockHandler, NotFoundHandler
from ssh.settings import (
    get_app_settings,  get_host_keys_settings, get_policy_setting,
    get_ssl_context, get_server_settings
)
from tornado.web import Application, FallbackHandler
from tornado.wsgi import WSGIContainer
from flask import Flask, render_template,request,jsonify
from ssh.main import make_app,app_listen
from RpiDetails import Details




flaskapp = Flask(__name__)


@flaskapp.route('/details')
def index():
    data = Details()
    return jsonify(data.Hostname())




if __name__ == '__main__':
    options.parse_command_line()
    container = WSGIContainer(flaskapp)
    loop = tornado.ioloop.IOLoop.current()
    host_keys_settings = get_host_keys_settings(options)
    policy = get_policy_setting(options, host_keys_settings)
    handlers = [
        (r'/ssh', IndexHandler, dict(loop=loop, policy=policy,
                                  host_keys_settings=host_keys_settings)),
        (r'/ssh/ws', WsockHandler, dict(loop=loop)),
        (r'.*', FallbackHandler, dict(fallback=container))
        
    ]
    app = make_app(handlers, get_app_settings(options))
    ssl_ctx = get_ssl_context(options)
    server_settings = get_server_settings(options)
    app_listen(app, options.port, options.address, server_settings)
    if ssl_ctx:
        server_settings.update(ssl_options=ssl_ctx)
        app_listen(app, options.sslport, options.ssladdress, server_settings)
    loop.start()
