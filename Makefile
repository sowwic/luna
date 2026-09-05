SHELL := /bin/bash

APP_NAME = puppet
DIST_DIR = dist
DIST_MAYA_MODULE_DIR = $(DIST_DIR)/maya_module
DIST_PYTHON_DIR = $(DIST_MAYA_MODULE_DIR)/python
DIST_plugins_DIR = $(DIST_MAYA_MODULE_DIR)/plugins
DIST_RESOURCES_DIR = $(DIST_MAYA_MODULE_DIR)/resources

BUILD_DIR = build
TEST_OUTPUT_DIR = .test_output


# Colors
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
MAGENTA := \033[35m
CYAN := \033[36m
RESET := \033[0m

# Banner helper
define banner
	@printf "$(CYAN)==>$(RESET) $(1)\n"
endef


.PHONY: help clean lint format pytest pytest-pdb mkdocs check build qrc venv
help:
	@echo "Available make targets:"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS=":.*?##"}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""

.PHONY: clean 
clean: ## Remove build artifacts, cache, and temporary files
	$(call banner, Cleaning project...)
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@rm -rf __pycache__
	@rm -rf .coverage
	@rm -rf src/**/__pycache__
	@rm -rf tests/**/__pycache__
	@rm -rf $(BUILD_DIR)
	@rm -rf $(DIST_DIR)
	@rm -rf $(TEST_OUTPUT_DIR)
	@printf "$(GREEN)Clean up complete.$(RESET)\n"

.PHONY: lint
lint: ## Run Ruff linter on source and tests
	$(call banner, Running Ruff linter...)
	@uv run ruff check src tests || true

.PHONY: format
format: ## Format source and tests with Ruff
	$(call banner, Running Ruff formatter...)
	@uv run ruff format src tests

.PHONY: pytest
pytest: ## Run tests using mayapy_test
	$(call banner, Running pytest...)
	@uv run ./mayapy_test tests

.PHONY: pytest-pdb
pytest-pdb: ## Run tests with pdb and clean output
	$(call banner, Cleaning pytest output dir...)
	@rm -rf $(TEST_OUTPUT_DIR)
	$(call banner, Running pytest with pdb...)
	@uv run ./mayapy_test --pdb tests

.PHONY: mkdocs
mkdocs: ## Start MkDocs documentation server
	$(call banner, Building MkDocs documentation...)
	@uv run mkdocs serve

.PHONY: check
check: lint pytest ## Run lint and tests

.PHONY: build
build: ## Build project package
	$(call banner, Building $(APP_NAME)...)
	@uv build


.PHONY: module-file
maya-module-file:  ## Generate dist/luna.mod
	@set -eu; \
	root="$$(pwd)"; \
	version="$$(tr -d '\r\n' < "$$root/VERSION")"; \
	module_root="$$root/dist/maya_module"; \
	mkdir -p "$$root/dist"; \
	printf '+ luna %s %s\nscripts: python\nplugins: plugins\n' \
		"$$version" "$$module_root" > "$$root/dist/luna.mod"

.PHONY: qrc
qrc: ## Generate QRC resources
	$(call banner, Generating QRC resources...)
	@pyside6-rcc resources/resources.qrc -o resources/resources_rc.py
	@printf "$(GREEN)QRC generation complete.$(RESET)\n"

.PHONY: venv
venv:  ## Recreate .venv using the Maya Python version
	@set -a; . ./.env; set +a; \
	: "$${MAYAPY:?Set MAYAPY in .env}"; \
	version="$$( "$$MAYAPY" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' )"; \
	printf '%s\n' "$$version" > .python-version; \
	unset VIRTUAL_ENV; \
	uv venv --clear

.PHONY: venv-shell
dev: venv  ## Create venv and enter it
	@. .venv/bin/activate && exec $$SHELL

.PHONY: build
dist: build  ## Generate dist/maya_module/luna.mod
	@rm -rf $(DIST_MAYA_MODULE_DIR)
	@mkdir -p $(DIST_PYTHON_DIR) $(DIST_PLUGINS_DIR) $(DIST_RESOURCES_DIR)
	@uv pip install --target $(DIST_PYTHON_DIR) dist/luna-*.whl
	@cp -R src/plugins/. $(DIST_PLUGINS_DIR)
	@cp -R src/resources/. $(DIST_RESOURCES_DIR)

.PHONY: install-module
install-module:  maya-module-file  ## Copy luna.mod to Maya's module directory
	@set -eu; \
	set -a; . ./.env; set +a; \
	: "$${MAYA_MODULE_PATH:?Set MAYA_MODULE_PATH in .env}"; \
	module_path="$${MAYA_MODULE_PATH%%:*}"; \
	mkdir -p "$$module_path"; \
	cp dist/luna.mod "$$module_path/luna.mod"; \
	printf 'Installed luna.mod in %s\n' "$$module_path"

.PHONY: install
install: dist install-module  ## Build package and install maya module
