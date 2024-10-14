# python-docker-boilerplate

Boilerplate code for starting a python project with docker and docker-compose

## How to set up your python environment

### Install python

On mac,

* You can read this blog to install python in a right way in
      python: https://opensource.com/article/19/5/python-3-default-mac
      
* **Recommendation**: Install python using brew and pyenv

### Managing python dependencies

* **Install poetry**

* On Mac OS, Windows and Linux,
  * Install poetry:
       * ``curl -sSL https://install.python-poetry.org | python3 -``
         * This way allows poetry and its dependencies to be isolated from your dependencies. I don't recommend to use 
         * pip to install poetry because poetry and your application dependencies will be installed in the same environment.
       * ```poetry init```: 
         * Use this command to set up your local environment, repository details, and dependencies. 
         * It will generate a pyproject.toml file with the information you provide.
           * Package name [python-starter]:
           * Version [0.1.0]:
           * Description []:
           * Author []:  n 
           * License []:
           * Compatible Python versions [^3.11]: 
           * Would you like to define your main dependencies interactively? (yes/no) [yes]: no
           * Would you like to define your development dependencies interactively? (yes/no) no
       * ```poetry install```: 
         * Use this command to automatically install the dependencies specified in the pyproject.toml file.
         * It will generate a poetry.lock file with the dependencies and their versions.
         * It will create a virtual environment in the home directory, e.g. /Users/user_name/Library/Caches/pypoetry/..
       * ```poetry env use python```: 
         * Use this command to find the virtual environment directory, created by poetry.
       * ```source ~/Library/Caches/pypoetry/virtualenvs/python-starter-0xoBsgdA-py3.11/bin/activate```
         * Use this command to activate the virtual environment.
       * ```poetry shell```: 
         * Use this command to activate the virtual environment.
       * ```poetry add pytest```: 
         * Use this command to add dependencies.
       * ```poetry add --dev pytest```:
         * Use this command to add development dependencies.
       * `` poetry update ``: 
         * Use this command if you change your .toml file and want to generate a new version the .lock file

## Set up in a docker environment

```
./init.sh
```

This will:

* copy the project folder
* build the docker image
* install the dependencies
* create a container with the application

## How to run the application

``docker compose exec app python --version``


## Tests

## Background
This repository goes with this documentation:
https://mlit.atlassian.net/wiki/spaces/LD/pages/10092544004/Python+in+LIT
