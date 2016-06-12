#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import psutil
import subprocess
import yaml

from flask import Flask
from flask import request

from two1.wallet.two1_wallet import Wallet
from two1.bitserv.flask import Payment

from cert21 import cert21

app = Flask(__name__)

# setup wallet
wallet = Wallet()
payment = Payment(app, wallet)

@app.route('/manifest')
def docs():
    """
    Provides the manifest.json file for the 21 endpoint crawler.
    """
    with open('./manifest.yaml', 'r') as f:
        manifest = yaml.load(f)
    return json.dumps(manifest)


@app.route('/')
@payment.required(50)
def cert():
    """ Runs cert on the provided url
    Returns: HTTPResponse 200 with a json containing the cert info.
    HTTP Response 400 if no uri is specified or the uri is malformed/cannot be reached.
    """
    try:
        uri = request.args['uri']
    except KeyError:
        return 'HTTP Status 400: URI query parameter is missing from your request.', 400

    try:
        data = cert21(uri)
        response = json.dumps(data, indent=4, sort_keys=True)
        return response
    except ValueError as e:
        return 'HTTP Status 400: {}'.format(e.args[0]), 400

if __name__ == "__main__":
    import click

    @click.command()
    @click.option("-d", "--daemon", default=False, is_flag=True,
                  help="Run in daemon mode.")
    @click.option("-D", "--debug", default=False, is_flag=True,
                  help="Run in debug mode.")
    def run(daemon, debug):
        if daemon:
            pid_file = './cert21.pid'
            if os.path.isfile(pid_file):
                pid = int(open(pid_file).read())
                os.remove(pid_file)
                try:
                    p = psutil.Process(pid)
                    p.terminate()
                except:
                    pass
            try:
                p = subprocess.Popen(['python3', 'cert21-server.py'])
                open(pid_file, 'w').write(str(p.pid))
            except subprocess.CalledProcessError:
                raise ValueError("error starting cert21-server.py daemon")
        else:
            print("Server running...")
            app.run(host='0.0.0.0', port=7002, debug=debug)

    run()
