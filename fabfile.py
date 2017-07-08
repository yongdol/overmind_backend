from fabric.api import env, sudo, run, local, cd, prompt

remote_git_repo = 'git@gitlab.com:sentience-dev/Friskweb-API.git'
remote_app_dir = 'friskweb/Friskweb-API'

env.hosts = ['fksrv@52.78.174.20:34288']
env.key_filename = '~/.ssh/id_rsa.pub'
env.warn_only = True


def create():
    # Install python, pip, virtualenv
    sudo('apt-get update')
    sudo('apt-get install -y python')
    sudo('apt-get install -y python-pip')
    sudo('apt-get install -y python-virtualenv')

    # Install flask with virtualenv
    with cd(remote_app_dir):
        sudo('virtualenv venv')
        sudo('source venv/bin/activate')
        sudo('pip install Flask')


def push():
    # Pushing from local to remote repository
    local('git pull')
    local('git add -A')
    commit_message = prompt("Commit message?")
    local('git commit -am "{0}"'.format(commit_message))
    local('git push')


def deploy():
    # Pull from remote repository & auto build
    with cd(remote_app_dir):
        run('git pull')
        run('source venv/bin/activate')
        run('pip install -r requirements.txt')
        run('apachectl restart')


def build():
    local('ssh fkdev2@52.78.174.20 -p 34288 -N -L 3306:127.0.0.1:3306 | python run.py')


def test():
    local('ssh fkdev2@52.78.174.20 -p 34288 -N -L 3306:127.0.0.1:3306 | pytest --pep8 backend/')
