#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Deployment toolkit.
'''

import os, re

from datetime import datetime
from fabric.api import *

env.user = 'root'
env.sudo_user = 'root'
env.hosts = ['121.42.34.63']

# 服务器MySQL用户名和口令:
db_user = 'root'
db_password = '449616a10e'

_TAR_FILE = 'dist-thinkpython.tar.gz'

_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE

_REMOTE_BASE_DIR = '/srv/thinkPython'

def _current_path():
    return os.path.abspath('.')

def _now():
    return datetime.now().strftime('%y-%m-%d_%H.%M.%S')

def backup(version):
    '''
    Dump entire database on server and backup to local.
    '''
    includes = ['www', 'log', 'run_web_server.py', 'run_task_server.py', 'run_tcp_server.py', 'run_creeper.py']
    excludes = ['test', '.*', '*.pyc', '*.pyo']
    with lcd(_current_path()):
        cmd = ['tar', '--dereference', '-czvf', '../dist/version-%s-%s' % (version , _TAR_FILE)]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))

def build():
    '''
    Build dist package.
    '''
    includes = ['www', 'log', 'run_web_server.py', 'run_task_server.py', 'run_tcp_server.py', 'run_creeper.py']
    excludes = ['test', '.*', '*.pyc', '*.pyo']
    local('rm -f dist/%s' % _TAR_FILE)
    with lcd(_current_path()):
        cmd = ['tar', '--dereference', '-czvf', './dist/%s' % _TAR_FILE]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))

def deploy():
    # 删除已有的tar文件:
    run('rm -f %s' % _REMOTE_TMP_TAR)
    # 上传新的tar文件:
    put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)
    # 删除原有www文件:
    with cd(_REMOTE_BASE_DIR):
        sudo('rm -r *')
    # 解压到新目录:
    with cd('%s' % _REMOTE_BASE_DIR):
        sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)
    # 重启Python服务和nginx服务器:
    with settings(warn_only=True):
        sudo('sudo supervisorctl reload')
        sudo('/etc/init.d/nginx reload')

def rollback(version):
    '''
    rollback to previous version
    '''
    _VERSION_REMOTE_TMP_TAR = '/tmp/version-%s-%s' % (version, _TAR_FILE)
    # 上传新的tar文件:
    put('dist/version-%s-%s' % (version, _TAR_FILE), _VERSION_REMOTE_TMP_TAR)
    # 删除原有www文件:
    with cd(_REMOTE_BASE_DIR):
        sudo('rm -r *')
    # 解压到新目录:
    with cd('%s' % _REMOTE_BASE_DIR):
        sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)
    # 重启Python服务和nginx服务器:
    with settings(warn_only=True):
        sudo('sudo supervisorctl reload')
        sudo('/etc/init.d/nginx reload')
    print ('ROLLBACKED OK.')
