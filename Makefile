.DEFAULT_GOAL := help

# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
SHELL := $(shell which bash)
DEFAULT_BRANCH := main
VERSION := 0.0.0
COMMIT := $(shell git rev-parse HEAD)
CDK := node_modules/.bin/cdk

CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
DEFAULT_BRANCH := main
DEFAULT_ENVIRONMENT := dev
PYTHON_VERSION := 3.10.6
CDK_VERSION := 2.70.0

help: ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

clean-venv: ## re-create virtual env
	[[ -e .venv ]] && rm -rf .venv; \
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python3 -m venv .venv; \
       source .venv/bin/activate; \
       pip install --upgrade pip setuptools; \
       pip install -r requirements.txt; \
    )

update_cdk_libs: ## install the latest version of aws cdk node and python packages
	bash scripts/update_cdk_libs.sh
	$(MAKE) clean-venv

install-cdk: ## install the latest cdk adn update the requirements
	( \
       scripts/update_cdk_libs.sh; \
    )

pylint: ## run pylint on python files
	( \
       . .venv/bin/activate; \
       git ls-files '*.py' | xargs pylint --max-line-length=90; \
    )

black: ## use black to format python files
	( \
       . .venv/bin/activate; \
       git ls-files '*.py' |  xargs black --line-length=79; \
    )

black-check: ## use black to format python files
	( \
       . .venv/bin/activate; \
       git ls-files '*.py' |  xargs black --check --line-length=79; \
    )

shellcheck: ## use black to format python files
	( \
       git ls-files 'scripts/*.sh' |  xargs shellcheck --format=gcc; \
    )

unittest: ## run test that don't require deployed resources
	( \
       source .venv/bin/activate; \
       python3 -m pytest -v -m "unit" tests/; \
    )

update_golden: ## update test golden files using the current actual results
	( \
       source .venv/bin/activate; \
       python3 -m pytest -v -m "unit" tests/ --update_golden; \
    )

validate_environment: ## validate environment data
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       source .venv/bin/activate; \
       PYTHONPATH="." python3 scripts/validate.py $(environment); \
    )

static: shellcheck black pylint unittest ## run all static checks

clean-cache: ## clean python adn pytest cache data
	@find . -type f -name "*.py[co]" -delete -not -path "./.venv/*"
	@find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} \;
	@rm -rf .pytest_cache

git-status: ## require status is clean so we can use undo_edits to put things back
	@status=$$(git status --porcelain); \
	if [ ! -z "$${status}" ]; \
	then \
		echo "Error - working directory is dirty. Commit those changes!"; \
		exit 1; \
	fi


rebase: git-status ## rebase current feature branch on to the default branch
	git fetch && git rebase origin/$(DEFAULT_BRANCH)

node_modules:
	bash scripts/update_cdk_libs.sh $(CDK_VERSION)
	$(MAKE) clean-venv

cdk-ls: node_modules ## run cdk ls
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) ls -c app_env=$(DEFAULT_ENVIRONMENT); \
    )

cdk-diff: node_modules ## run cdk diff
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) diff $(stack) -c app_env=$(DEFAULT_ENVIRONMENT); \
    )

cdk-synth: node_modules ## run cdk synth
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) synth $(stack) -c app_env=$(DEFAULT_ENVIRONMENT); \
    )

cdk-deploy: node_modules ## run cdk deploy
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	# source the pyenv config script
	# set the local pythin version. redundant but harmless
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) deploy --require-approval never $(stack) -c app_env=$(DEFAULT_ENVIRONMENT); \
    )

cdk-destroy: node_modules ## run cdk deploy
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	# source the pyenv config script
	# set the local pythin version. redundant but harmless
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) destroy --force $(stack) -c app_env=$(DEFAULT_ENVIRONMENT); \
    )

python_script: ## run python script
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       PYTHONPATH="." python3 $(SCRIPT); \
    )

.PHONY: build static test artifact	
