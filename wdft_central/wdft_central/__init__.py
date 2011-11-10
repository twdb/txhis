import os
import socket

import app

if socket.gethostname() == 'Midgewater':
    DEPLOYED = True
else:
    DEPLOYED = False

if DEPLOYED:
    DEPLOYMENT_DIR = '/space/www/wdft_central/'
else:
    DEPLOYMENT_DIR = os.path.abspath('../')

DATABASE_URI = 'sqlite:////' + os.path.join(
    DEPLOYMENT_DIR, 'data/', "HisCentralRegisterFinalDBFile.db")


application = app.create_app(DATABASE_URI)

if __name__ == '__main__':
    try:
        from wsgiref.simple_server import make_server
        server = make_server('localhost', 7789, application)
        server.serve_forever()
    except ImportError:
        print "Error: example server code requires Python >= 2.5"
