# Makefile to gather common commands

.PHONY: build check clean docker-build-dev docker-build-prod docker-open-shell docker-run-dev docker-scan docker-test format help lint pipenv-dev-install run-dev run-prod test version
.DEFAULT_GOAL := help

# Project variables
SRC:=src

# Command overrides
# In docker-related commands, provide DOCKER=podman to use podman instead of docker
DOCKER:=docker

# Fetch from git tags the current dev version string, if not found use seconds since epoch
TAG := $(shell git describe --tags --always --dirty --broken 2>/dev/null || date +%s)

help: ## Show this help menu
	$(info Available make commands:)
	@grep -e '^[a-z|_|-]*:.* ##' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS=":.* ## "}; {printf "\t%-23s %s\n", $$1, $$2};'

.print-phony:
	@echo -n "\n.PHONY: "
	@grep '^[a-z|_|-]*:.* ##' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS=":.* ## "}; {printf "%s ", $$1};'
	@echo "\n"

####### COMMANDS #######################################################################

check: ## Check source-code for known security vulnerabilities
	$(info Checking code for known security vulnerabilities...)
	@pipenv check
	@echo Done.

clean: ## Clean up auxiliary and temporary files from the workspace
	$(info Cleaning auxiliary and temporary files...)
	@find . -maxdepth 1 -type d -name '.mypy_cache' -exec rm -r {} +
	@find . -maxdepth 1 -type d -name '.ruff_cache' -exec rm -r {} +
	@find . -maxdepth 1 -type d -name 'build'       -exec rm -r {} +
	@find . -maxdepth 1 -type d -name 'dist'        -exec rm -r {} +
	@find . -maxdepth 2 -type d -name '*.egg-info'  -exec rm -r {} +
	@echo Done.

format: ## Format the entire codebase
	@if \
	type black >/dev/null 2>&1 ; then \
		echo Formatting source-code... && \
		echo Applying black... && \
		black $(SRC) tests && \
		echo Done. ; \
	else echo SKIPPED. Run 'make pipenv-dev-install' first. >&2 ; fi

lint: ## Perform a static code analysis
	@if \
	type ruff >/dev/null 2>&1 && \
	type mypy >/dev/null 2>&1 ; then \
		echo Linting source-code... && \
		echo Applying ruff... && \
		ruff $(SRC) tests && \
		echo Applying mypy... && \
		mypy --show-error-context --show-column-numbers --pretty $(SRC) tests && \
		echo Done. ; \
	else echo SKIPPED. Run 'make pipenv-dev-install' first. >&2 ; fi

pipenv-dev-install: ## Create dev venv
	@pipenv run pip install --upgrade pip
	@pipenv install --dev --ignore-pipfile --deploy

####### COMMANDS - MAIN #######################################################################

d-create-network: ## Create internal network
	@docker network create dataplaynet || true

dcomp-up: d-create-network ## Start all services
	@docker-compose up -d

dcomp-up-mongo: d-create-network ## Start mongo service
	@docker-compose --profile mongo up -d

dcomp-down: ## Stop all services
	@docker-compose down
