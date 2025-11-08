# Set global variables
remote?=none
dev?=False

# Colors
CYAN:=\033[36m
NC:=\033[0m
PURPLE:=\033[35m
VENV_DIR:=.venv
YELLOW:=\033[33m


.PHONY: help venv install permissions gitinit gitcommit dkinit dkup dkdown dkrestart test

# Set main functions
help: ## Show this help
	@echo "\n$(PURPLE)⚠️  NOTICE: All next commands are for Linux$(NC)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo "\n"


venv: ## Create new virtual environment
	@echo "\n$(YELLOW)WARNING: Make sure 'Venv' is installed before create a new virtual environment!$(NC)"
	@if [ ! -d $(VENV_DIR) ]; then \
		echo "\n🛠  Creating a new virtual environment with 'Venv'..."; \
		python3 -m venv $(VENV_DIR) && \
		echo "✅  Virtual environment ready to activate!" && \
		echo "👉  Please, run $(CYAN)'source $(VENV_DIR)/bin/activate'$(NC)...\n"; \
	else \
		echo "\n✅  '$(VENV_DIR)' already exists!"; \
		echo "Make sure it is active! 😊\n"; \
	fi


install: ## Install project dependencies
	@if [ -f requirements.txt ]; then \
		if [ "$$(which python)" = "$$(realpath -s $(VENV_DIR)/bin/python)" ]; then \
			echo "\n⏰  Preparing all requirements...\n"; \
			$(VENV_DIR)/bin/pip install --upgrade pip -q; \
			$(VENV_DIR)/bin/pip install -r requirements.txt && \
			echo "\n📦  All requirements ready!\n"; \
		else \
			echo "\n⚠️  Activate virtual environment before install dependencies!"; \
			echo "👉  Please, run $(CYAN)'source $(VENV_DIR)/bin/activate'$(NC) to activate virtual environment...\n"; \
		fi; \
	else \
		echo "\n$(YELLOW)WARNING: ℹ  There is no requirements file! The program could fail while running... 😱 Make sure it no needs any requirement before run!$(NC)\n"; \
	fi

permissions: ## Create necessary folders & set permissions
	@echo "\n🔑  Setting up permissions..."
	@./permissions.sh && echo "✅  Starting project...\n"

gitinit: ## Do first commit & push-it
	@if [ $(remote) != 'none' ]; then \
		echo "\n✅  Starting version control..."; \
		git init && \
		git branch -M main && \
		git add . && \
		git commit -m "Initial commit"; \
		if ! git remote | grep -q origin; then \
			git remote add origin $(remote); \
			echo "\n🔗️  Git remote added!"; \
		else \
			echo "\nℹ  Git remote already exists!"; \
		fi; \
		echo "\n📤 Ready to push!"; \
		git push -u origin main && \
		echo "\n🎉🎉 Congratulations! All elements uploaded! 🎉🎉\n"; \
	else \
		echo "\n⚠️  No git remote added! The current variable is '$(remote)'..."; \
		echo "👉  Please, run the command as it follows:"; \
		echo "$(CYAN)    make gitinit remote=https://github.com/your_username/your_repo$(NC)\n"; \
	fi


gitcommit: ## Create new commit
	@if [ -d '.git' ]; then \
		echo "\n🏁  creating new check-point!"; \
		git add . && \
		git commit -m "Check-point at $(shell date "+%d-%m-%Y %H:%M:%S")" --allow-empty && \
		echo "🏁  New check-point added!\n"; \
	else \
		echo "\n⚠️  Ops! You need to initiate Git before create a new check-point!\n"; \
		exit 1; \
	fi


dkinit: permissions ## Prepare docker
	@echo "\n🚀  Starting docker checker..."
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "👉  Ops! It seems Docker is not installed on your system. Please install it and come back again...\n"; \
		exit 1; \
	else \
		echo "Nice! Docker is installed! 😎"; \
		echo "Docker commands are now available!\n"; \
	fi


dkup: dkinit ## Start docker services
	@if [ $(dev) = 'True' ]; then \
		echo "\n👀  ...Starting docker services in DEBUG mode... 👀"; \
		docker compose -f compose.yaml up; \
	else \
		echo "\n🐋  ...Starting docker services... 🐋"; \
		docker compose -f compose.yaml up -d; \
	fi


dkdown: dkinit ## Stop docker services
	@echo "\n🐋  ...Closing docker services... 🐋"
	@docker compose -f compose.yaml down


dkrestart: dkinit ## Restart docker services
	@echo "\n👀  Restarting docker services... \n"
	@$(MAKE) dkdown
	@if [ $(dev) = 'True' ]; then \
		echo "\n👀  ...Starting docker services in DEBUG mode... 👀"; \
		docker compose -f compose.yaml up; \
	else \
		echo "\n🐋  ...Starting docker services... 🐋"; \
		docker compose -f compose.yaml up -d; \
	fi


test: ## Run module tests
	@echo "\n🧪  Running Music Manager tests... \n"
	@docker compose run --rm odoo --test-enable --test-tags /music_manager --stop-after-init
