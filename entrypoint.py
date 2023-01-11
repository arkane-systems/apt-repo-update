import os
import git
import gnupg
import json
import logging
import pathlib
import re
import shutil
import sys

from debian.debfile import DebFile

debug = os.environ.get("INPUT_DEBUG", False)

if debug:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
else:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

if __name__ == "__main__":
    logging.info("-- Parsing input --")

    github_token = os.environ.get("INPUT_GITHUB_TOKEN")
    supported_arch = os.environ.get("INPUT_REPO_SUPPORTED_ARCH")
    supported_distro = os.environ.get("INPUT_REPO_SUPPORTED_DISTRO")

    github_repo = os.environ.get("GITHUB_REPOSITORY")

    git_commit_message = os.environ.get(
        "INPUT_GIT_COMMIT_MESSAGE",
        "[apt-action] Update apt repo with last pushed updates.",
    )
    git_push_branch = os.environ.get("INPUT_GIT_PUSH_BRANCH", "master")

    apt_folder = os.environ.get("INPUT_REPO_DIRECTORY", "apt")
    update_folder = os.environ.get("INPUT_UPDATE_DIRECTORY", "updates")

    if None in (github_token, supported_arch, supported_distro):
        logging.error("Required key is missing")
        sys.exit(1)

    supported_arch_list = supported_arch.strip().split("\n")
    supported_distro_list = supported_distro.strip().split("\n")

    logging.debug(supported_arch_list)
    logging.debug(supported_distro_list)

    key_private = os.environ.get("INPUT_PRIVATE_KEY")
    key_passphrase = os.environ.get("INPUT_KEY_PASSPHRASE")

    logging.info("-- Done parsing input --")

    # Clone repo

    logging.info("-- Cloning current Github page --")

    github_user = github_repo.split("/")[0]
    github_slug = github_repo.split("/")[1]

    if os.path.exists(github_slug):
        shutil.rmtree(github_slug)

    git_repo = git.Repo.clone_from(
        "https://{}@github.com/{}.git".format(github_token, github_repo),
        github_slug,
    )

    git_refs = git_repo.remotes.origin.refs
    git_refs_name = list(map(lambda x: str(x).split("/")[-1], git_refs))

    if git_repo.head.commit.author.email == "{}@users.noreply.github.com".format(
        github_user
    ):
        logging.info("Last commit was by this action; nothing to do")
        sys.exit(0)

    logging.debug(git_refs_name)

    logging.info("-- Done cloning current Github page --")

    # Set directories
    update_dir = os.path.abspath(os.path.join(github_slug, update_folder))
    apt_dir = os.path.abspath(os.path.join(github_slug, apt_folder))

    # Prepare key

    logging.info("-- Importing and preparing GPG key --")

    gpg = gnupg.GPG()
    private_import_result = gpg.import_keys(key_private)

    if private_import_result.count != 1:
        logging.error("Invalid private key provided; please provide 1 valid key.")
        sys.exit(1)

    logging.debug(private_import_result)

    if not any(data["ok"] >= "16" for data in private_import_result.results):
        logging.error("Key provided is not a secret key")
        sys.exit(1)

    private_key_id = private_import_result.results[0]["fingerprint"]

    logging.info("-- Done importing key --")

    # Process files.

    logging.info("-- Processing updates --")

    os.chdir(update_dir)

    # Enumerate and add files (deb packages).

    files = [
        f
        for f in os.listdir()
        if os.path.isfile(f) and pathlib.Path(f).suffix == ".deb"
    ]

    if len(files) == 0:
        logging.info("Nothing to do")
        sys.exit(0)

    for file in files:
        for distro in supported_distro_list:
            # Add to repo
            logging.info("Adding binary package {} to repo {}".format(file, distro))

            os.system(
                "reprepro -b {} --export=silent-never includedeb {} {}".format(
                    apt_dir, distro, file
                )
            )

        os.remove(file)

    # TODO: handle source (dsc) packages

    # Exporting and signing repo

    logging.info("-- Exporting and signing repo --")

    gpg.sign("test", keyid=private_key_id, passphrase=key_passphrase)

    os.system("reprepro -b {} export".format(apt_dir))

    logging.info("-- Done exporting and signing repo --")

    # Commiting and push changes

    logging.info("-- Saving changes --")

    git_repo.config_writer().set_value(
        "user", "email", "{}@users.noreply.github.com".format(github_user)
    )

    git_repo.git.add("*")
    git_repo.index.commit(git_commit_message)

    git_repo.git.push("--set-upstream", "origin", git_push_branch)

    logging.info("-- Done saving changes --")
