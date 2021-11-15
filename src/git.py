import subprocess

def git_status(path):
    try:
       current = subprocess.check_output(['git', '-C', '{0}/'.format(path), 'rev-parse', 'HEAD']).strip().decode('UTF-8')
       remote = subprocess.check_output('git -C {0} ls-remote --heads --quiet | cut -f1'.format(path), shell=True).strip().decode('UTF-8')

       if current == remote:
          return "- Updated (Git)"
       else:
          return "- There is a new version (Git)"
    except:
       return ''

def git_version(path):
    try:
        version = subprocess.check_output(['git', '-C', '{0}/'.format(path),'log', '-n', '1', '--pretty=tformat:%h']).strip().decode('UTF-8')
    except:
        version = '0b'
    finally:
        return version

def git_pull(path):
    current = subprocess.check_output(['git', '-C', '{0}'.format(path), 'rev-parse', 'HEAD']).strip().decode('UTF-8')
    remote = subprocess.check_output('git -C {0} ls-remote --heads --quiet | cut -f1'.format(path), shell=True).strip().decode('UTF-8')

    print('Local version:  [{0}]\Remote version: [{1}]'.format(current,remote))

    git_fetch = subprocess.check_output('git -C {0} fetch --all'.format(path), shell=True).strip().decode('UTF-8')
    print(git_fetch)
    git_reset = subprocess.check_output('git -C {0} reset --hard origin/master'.format(path), shell=True).strip().decode('UTF-8')
    print(git_reset)
    git_pull = subprocess.check_output('git -C {0} pull origin master'.format(path), shell=True).strip().decode('UTF-8')
    print(git_pull)
