PACKAGES := clinicadl tests
PIP ?= pip
POETRY ?= poetry
CONDA ?= conda
CONDA_ENV ?= "./env"
DATA_CI := "/Users/thibault.devarax/Desktop/code/clinicadl_data_ci/data_ci"

.PHONY: help
help: Makefile
	@echo "Commands:"
	@sed -n 's/^##//p' $<

.PHONY: check.lock
check.lock:
	@$(POETRY) check --lock

## build			: Build the package.
.PHONY: build
build:
	@$(POETRY) build

.PHONY: clean.doc
clean.doc:
	@$(RM) -rf site

.PHONY: clean.test
clean.test:
	@$(RM) -r .pytest_cache/

## doc			: Build the documentation.
.PHONY: doc
doc: clean.doc env.doc
	@$(POETRY) run mkdocs build

## env			: Bootstrap an environment.
.PHONY: env
env: env.dev

.PHONY: env.conda.create
env.conda.create:
	@$(CONDA) env create -p $(CONDA_ENV)/$(ENV_NAME) -k

.PHONY: env.conda.clean
env.conda.clean:
	@rm -rf $(CONDA_ENV)

.PHONY: env.dev
env.dev:
	@$(POETRY) install

.PHONY: env.doc
env.doc:
	@$(POETRY) install --extras docs

## format			: Format the codebase.
.PHONY: format
format: format.black format.isort

.PHONY: format.black
format.black: env.dev
	@$(POETRY) run black --quiet $(PACKAGES)

.PHONY: format.isort
format.isort: env.dev
	@$(POETRY) run isort --quiet $(PACKAGES)

## lint			: Lint the codebase.
.PHONY: lint
lint: lint.black lint.isort

.PHONY: lint.black
lint.black: env.dev
	@$(POETRY) run black --check --diff $(PACKAGES)

.PHONY: lint.isort
lint.isort: env.dev
	@$(POETRY) run isort --check --diff $(PACKAGES)

## Install
.PHONY: install
install: check.lock
	@$(POETRY) install

.PHONY: install.dev
install.dev: check.lock
	@$(POETRY) install --only dev

.PHONY: install.doc
install.doc: check.lock
	@$(POETRY) install --only docs

.PHONY: install.functional-tests
install.functional-tests: env.conda.create
	@$(CONDA) run -p $(CONDA_ENV)/$(ENV_NAME) pip install -r $(REQ_FILE)

## tests
.PHONY: unit-tests
unit-tests: install
	@$(POETRY) run python -m pytest -v -m "not gpu and not multi_gpu" tests/unittests

.PHONY: gpu-unit-tests
gpu-unit-tests: install
	@$(POETRY) run python -m pytest -v -m "gpu" tests/unittests

.PHONY: multi-gpu-unit-tests
multi-gpu-unit-tests: install
	@$(POETRY) run python -m pytest -v -m "multi_gpu" tests/unittests

.PHONY: functional-tests
functional-tests: install
	@$(POETRY) run python -m pytest -v -m "not gpu and not multi_gpu" --ref /localdrive10TB/users/clinicadl.ci/clinicadl_data_ci/data_ci tests/functional

.PHONY: gpu-functional-tests
gpu-functional-tests: install
	@$(POETRY) run python -m pytest -v -m "gpu" --ref /localdrive10TB/users/clinicadl.ci/clinicadl_data_ci/data_ci tests/functional

.PHONY: which-python
which-python: install.functional-tests
which-python:
	@$(CONDA) run -p $(CONDA_ENV)/$(ENV_NAME) which clinicadl

.PHONY: functional-test-segmentation
functional-test-segmentation: ENV_NAME := classification
functional-test-segmentation: REQ_FILE := $(DATA_CI)/maps_test_segmentation/environment.txt
functional-test-segmentation: which-python
	@$(CONDA) run -p $(CONDA_ENV)/$(ENV_NAME) python -m pytest -v -m "not gpu" --ref $(DATA_CI) tests/functional/test_segmentation.py