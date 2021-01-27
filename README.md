# apt-repo-update
GitHub action to automatically update an apt repository (located in the master branch) with new packages.

Very loosely based on https://github.com/jrandiny/apt-repo-action

## Configuration

**debug***

[Not required] Print debugging information (true/false**.

**github_token**

A personal access token to the repo with commit and push scope. Use a repository secret.

**repo_supported_arch**

Newline-delimited list of supported architectures.

**repo_supported_distro**

Newline-delimited list of supported distributions. Note: update packages will be added to the repository for all of these distributions automatically.

**repo_directory**

Location of the APT repo folder relative to the Git repo root. The APT repository must already exist; this action will not create it for you. Defaults to "apt" if not specified.

**update_directory**

Location of the update folder relative to the Git repo root. Packages placed in this directory and committed will automatically be added to the repository and deleted from this folder when the action runs. Defaults to "updates** if not specified.

**private_key**

GPG private key (in ascii-armored format) for signing the APT repository. Use a repository secret.

**key_passphrase**

Passphrase of the above private key.

## Sample Workflow

```
name: Publish new packages.

# Controls when the action will run.
on:
  # Triggers the workflow on push events but only for the master branch
  push:
    branches: [ master ]

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:
  # This workflow contains a single job called "build"
  publish:
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:
      # Runs a single command using the runners shell
      - uses: arkane-systems/apt-repo-update@v1.1
        with:
          debug: false
          github_token: ${{ secrets.PAT }}
          repo_supported_arch: |
            amd64
          repo_supported_distro: |
            focal
            bionic
            buster
            bullseye
            bookworm
            sid
          private_key: ${{ secrets.PRIVATE }}
          key_passphrase: ${{ secrets.SECRET }}
```
