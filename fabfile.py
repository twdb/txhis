import os

from fabric.api import *

# the user to use for the remote commands
env.user = 'wdft'

# the servers where the commands are executed
env.hosts = ['midgewater.twdb.state.tx.us:22222']

WOFPY_DEPLOYMENTS_DIR = '/space/www/wofpy_deployments/'
CENTRAL_REGISTRY_DEPLOYMENTS_DIR = '/space/www/'


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


def deploy_tpwd():
    pack('tpwd')
    deploy('tpwd')
    copy_cache_file('tpwd', 'tpwd_pyhis_cache.db')


def pack(app):
    """creates new source distribution as tarball"""
    local_app_dir = os.path.join('wofpy_deployments', app + '_deployment')
    with lcd(local_app_dir):
        local('python setup.py sdist --formats=gztar', capture=False)


def deploy(app):
    """deploys an application"""
    local_app_dir = os.path.join('wofpy_deployments', app + '_deployment')
    remote_app_dir = os.path.join(WOFPY_DEPLOYMENTS_DIR,
                                  app + '_deployment')
    deployment_python = os.path.join('/space/www/wsgi_env/bin/python')

    # figure out the release name and version
    with lcd(local_app_dir):
        dist = local('python setup.py --fullname', capture=True).strip()
    wsgi_dir = 'wsgi'
    wsgi_conf_file = app + '_apache_wsgi.conf'
    remote_wsgi_conf_file = os.path.join(remote_app_dir, wsgi_conf_file)
    app_conf_file = app + '_config.cfg'
    # calculate file paths
    dist_tar = '%s.tar.gz' % dist
    temp_remote_install_dir = os.path.join('/tmp', local_app_dir)
    temp_dist_tar = os.path.join('/tmp', dist_tar)
    # upload the source tarball to the temporary folder on the server
    put(os.path.join(local_app_dir, 'dist', dist_tar),
        temp_dist_tar)
    # create a place where we can unzip the tarball, then enter
    # that directory and unzip it
    run('mkdir -p %s' % temp_remote_install_dir)
    with cd(temp_remote_install_dir):
        run('tar -xzf %s' % temp_dist_tar)
    # now setup the package with our virtual environment's python
    # interpreter
    with cd(os.path.join(temp_remote_install_dir, dist)):
        run(deployment_python + ' setup.py install')
    # now that all is set up, delete the folder again
    run('rm -rf %s %s' % (temp_dist_tar, temp_remote_install_dir))
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
    with lcd(local_app_dir):
        put(wsgi_dir, remote_app_dir)
        put(wsgi_conf_file, remote_wsgi_conf_file)
        put(app_conf_file, remote_app_dir)


def build_cbi_cache():
    """runs the build_cbi_cache script on the remote machine"""
    deployment_name = 'cbi_deployment'
    local_app_dir = os.path.join('wofpy_deployments', deployment_name)
    remote_app_dir = os.path.join(WOFPY_DEPLOYMENTS_DIR,
                                  deployment_name)
    # deployment_python = os.path.join(remote_app_dir,
    #                                  'cbi_env/bin/python')
    cbi_cache_dir = '/space/www/wofpy_deployments/cbi_deployment/cache/'

    with lcd(local_app_dir):
        put('cbi/build_cbi_cache.py', remote_app_dir)
        put('cbi/cbi_cache_models.py', remote_app_dir)

    with cd(remote_app_dir):
        run('mkdir -p %s' % cbi_cache_dir)
        run('python %s/build_cbi_cache.py --dropall True' % remote_app_dir)


def copy_cache_file(app, cache_file):
    """runs the build_cbi_cache script on the remote machine"""
    deployment_name = app + '_deployment'
    local_app_dir = os.path.join('wofpy_deployments', deployment_name)
    remote_app_dir = os.path.join(WOFPY_DEPLOYMENTS_DIR,
                                  deployment_name)
    # deployment_python = os.path.join(remote_app_dir,
    #                                  'cbi_env/bin/python')
    remote_cache_dir = os.path.join(remote_app_dir, 'cache/')
    local_cache_dir = os.path.join(local_app_dir, 'cache/')

    get_filesize_command = "du -b %s | awk '{print $1}'" % cache_file

    with cd(remote_cache_dir):
        remote_size = run(get_filesize_command)

    with lcd(local_cache_dir):
        local_size = local(get_filesize_command, capture=True)
        if local_size != remote_size:
            put(cache_file, remote_cache_dir)


def deploy_central():
    """deploys an application"""
    deployment_name = 'wdft_central'
    local_app_dir = os.path.join('wofpy_deployments', deployment_name)
    with lcd(local_app_dir):
        local('python setup.py sdist --formats=gztar', capture=False)

    remote_app_dir = os.path.join(CENTRAL_REGISTRY_DEPLOYMENTS_DIR,
                                  local_app_dir,)
    deployment_python = os.path.join('/space/www/wsgi_env/bin/python')

    # figure out the release name and version
    with lcd(local_app_dir):
        dist = local('python setup.py --fullname', capture=True).strip()
    wsgi_dir = 'wsgi'
    wsgi_conf_file = 'wdft_central_apache_wsgi.conf'
    remote_wsgi_conf_file = os.path.join(remote_app_dir, wsgi_conf_file)

    # calculate file paths
    dist_tar = '%s.tar.gz' % dist
    temp_remote_install_dir = os.path.join('/tmp', local_app_dir)
    temp_dist_tar = os.path.join('/tmp', dist_tar)
    # upload the source tarball to the temporary folder on the server
    put(os.path.join(local_app_dir, 'dist', dist_tar),
        temp_dist_tar)
    # create a place where we can unzip the tarball, then enter
    # that directory and unzip it
    run('mkdir -p %s' % temp_remote_install_dir)
    with cd(temp_remote_install_dir):
        run('tar -xzf %s' % temp_dist_tar)
    # now setup the package with our virtual environment's python
    # interpreter
    with cd(os.path.join(temp_remote_install_dir, dist)):
        run(deployment_python + ' setup.py install')
    # now that all is set up, delete the folder again
    run('rm -rf %s %s' % (temp_dist_tar, temp_remote_install_dir))
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
    with lcd(local_app_dir):
        put(wsgi_dir, remote_app_dir)
        put(wsgi_conf_file, remote_wsgi_conf_file)
