import os
import git
import gnupg
import json
import logging
import re
import shutil

from debian.debfile import DebFile

debug = os.environ.get('INPUT_DEBUG', False)

if debug:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

if __name__ == '__main__':
    logging.info('-- Parsing input --')

    github_token = os.environ.get('INPUT_GITHUB_TOKEN')
    supported_arch = os.environ.get('INPUT_REPO_SUPPORTED_ARCH')
    supported_distro = os.environ.get('INPUT_REPO_SUPPORTED_DISTRO')

    github_repo = os.environ.get('GITHUB_REPOSITORY')

    apt_folder = os.environ.get('INPUT_REPO_DIRECTORY', 'apt')
    update_folder = os.environ.get('INPUT_UPDATE_DIRECTORY', 'updates')

    if None in (github_token, supported_arch, supported_distro):
        logging.error('Required key is missing')
        sys.exit(1)

    supported_arch_list = supported_arch.strip().split('\n')
    supported_distro_list = supported_distro.strip().split('\n')

    logging.debug(github_token)
    logging.debug(supported_arch_list)
    logging.debug(supported_distro_list)

#    key_public = os.environ.get('INPUT_PUBLIC_KEY')
#    key_private = os.environ.get('INPUT_PRIVATE_KEY')
#    key_passphrase = os.environ.get('INPUT_KEY_PASSPHRASE')

#    logging.debug(key_public)
#    logging.debug(key_private)
#    logging.debug(key_passphrase)

#    logging.info('-- Done parsing input --')

    # Clone repo

    logging.info('-- Cloning current Github page --')

    github_user = github_repo.split('/')[0]
    github_slug = github_repo.split('/')[1]

    if os.path.exists(github_slug):
        shutil.rmtree(github_slug)

    git_repo = git.Repo.clone_from(
        'https://{}@github.com/{}.git'.format(github_token, github_repo),
        github_slug,
    )

    git_refs = git_repo.remotes.origin.refs
    git_refs_name = list(map(lambda x: str(x).split('/')[-1], git_refs))

    logging.debug(git_refs_name)

    logging.info('-- Done cloning current Github page --')

    # Process files.

    logging.info('-- Processing updates --')

    # Generate metadata
    os.chdir(github_slug + '/' + update_folder)
    logging.debug(os.listdir())