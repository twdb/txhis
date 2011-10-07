import os

from fabric.api import *

# the user to use for the remote commands
env.user = 'wdft'

# the servers where the commands are executed
env.hosts = ['midgewater.twdb.state.tx.us:22222']

WOFPY_DEPLOYMENTS_DIR = '/space/www/wofpy_deployments/'


def pack_cbi():
    pack('cbi')


def deploy_cbi():
    pack('cbi')
    deploy('cbi')
    build_cbi_cache()


def deploy_tceq():
    pack('tceq')
    deploy('tceq')
    copy_cache_file('tceq', 'tceq_pyhis_cache.db')


def pack(app):
    """creates new source distribution as tarball"""
    deployment_app = app + '_deployment'
    with lcd(deployment_app):
        local('python setup.py sdist --formats=gztar', capture=False)


def deploy(app):
    """deploys an application"""
    deployment_app = app + '_deployment'
    deployment_dir = os.path.join(WOFPY_DEPLOYMENTS_DIR,
                                  deployment_app,)
    deployment_python = os.path.join('/space/www/wsgi_env/bin/python')

    # figure out the release name and version
    with lcd(deployment_app):
        dist = local('python setup.py --fullname', capture=True).strip()
    wsgi_dir = 'wsgi'
    wsgi_conf_file = app + '_apache_wsgi.conf'
    remote_wsgi_conf_file = os.path.join(deployment_dir, wsgi_conf_file)
    app_conf_file = os.path.join(app, app + '_config.cfg')
    # calculate file paths
    dist_tar = '%s.tar.gz' % dist
    temp_deployment_app = os.path.join('/tmp', deployment_app)
    temp_dist_tar = os.path.join('/tmp', dist_tar)
    # upload the source tarball to the temporary folder on the server
    put(os.path.join(deployment_app, 'dist', dist_tar),
        temp_dist_tar)
    # create a place where we can unzip the tarball, then enter
    # that directory and unzip it
    run('mkdir -p %s' % temp_deployment_app)
    with cd(temp_deployment_app):
        run('tar -xzf %s' % temp_dist_tar)
    # now setup the package with our virtual environment's python
    # interpreter
    with cd(os.path.join(temp_deployment_app, dist)):
        run(deployment_python + ' setup.py install')
    # now that all is set up, delete the folder again
    run('rm -rf %s %s' % (temp_dist_tar, temp_deployment_app))
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
    with lcd(deployment_app):
        put(wsgi_dir, deployment_dir)
        put(wsgi_conf_file, remote_wsgi_conf_file)
        put(app_conf_file, deployment_dir)


def build_cbi_cache():
    """runs the build_cbi_cache script on the remote machine"""
    deployment_app = 'cbi_deployment'
    deployment_dir = os.path.join(WOFPY_DEPLOYMENTS_DIR,
                                  deployment_app,)
    # deployment_python = os.path.join(deployment_dir,
    #                                  'cbi_env/bin/python')
    cbi_cache_dir = '/space/www/wofpy_deployments/cbi_deployment/cache/'

    with lcd(deployment_app):
        put('cbi/build_cbi_cache.py', deployment_dir)
        put('cbi/cbi_cache_models.py', deployment_dir)

    with cd(deployment_dir):
        run('mkdir -p %s' % cbi_cache_dir)
        run('python %s/build_cbi_cache.py --dropall True' % deployment_dir)


def copy_cache_file(app, cache_file):
    """runs the build_cbi_cache script on the remote machine"""
    deployment_app = app + '_deployment'
    deployment_dir = os.path.join(WOFPY_DEPLOYMENTS_DIR,
                                  deployment_app,)
    # deployment_python = os.path.join(deployment_dir,
    #                                  'cbi_env/bin/python')
    remote_cache_dir = os.path.join(deployment_dir, 'cache/')
    local_cache_dir = os.path.join(deployment_app, 'cache/')

    get_filesize_command = "du -b %s | awk '{print $1}'" % cache_file

    with cd(remote_cache_dir):
        remote_size = run(get_filesize_command)

    with lcd(local_cache_dir):
        local_size = local(get_filesize_command, capture=True)
        if local_size != remote_size:
            put(cache_file, remote_cache_dir)
