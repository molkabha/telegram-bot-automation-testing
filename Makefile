# Telegram Bot Automation Testing Framework - Makefile
# Professional automation commands for development and testing

.PHONY: help install install-dev setup clean test test-smoke test-api test-ui test-all
.PHONY: lint format type-check security-check quality-check
.PHONY: docker-build docker-test docker-smoke docker-clean
.PHONY: reports serve-docs coverage
.PHONY: ci-setup ci-test deploy

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
PYTEST := python -m pytest
DOCKER := docker
DOCKER_COMPOSE := docker-compose
PROJECT_NAME := telegram-bot-test-framework
IMAGE_NAME := $(PROJECT_NAME):latest
REPORTS_DIR := reports
SCREENSHOTS_DIR := screenshots
LOGS_DIR := logs

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Telegram Bot Automation Testing Framework$(NC)"
	@echo "$(BLUE)=========================================$(NC)"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make install          # Install dependencies"
	@echo "  make test-smoke       # Run smoke tests"
	@echo "  make docker-test      # Run tests in Docker"
	@echo "  make quality-check    # Run all quality checks"

# Installation and Setup
install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Production dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install black flake8 mypy bandit safety pytest-cov pre-commit
	@echo "$(GREEN)✅ Development dependencies installed$(NC)"

setup: install-dev ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@mkdir -p $(REPORTS_DIR) $(SCREENSHOTS_DIR) $(LOGS_DIR)
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env template...$(NC)"; \
		echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env; \
		echo "TELEGRAM_BOT_USERNAME=@your_bot_username" >> .env; \
		echo "TELEGRAM_TEST_CHAT_ID=your_chat_id_here" >> .env; \
		echo "HEADLESS=true" >> .env; \
		echo "$(YELLOW)⚠️  Please update .env with your bot credentials$(NC)"; \
	fi
	pre-commit install 2>/dev/null || echo "$(YELLOW)Pre-commit hooks installation skipped$(NC)"
	@echo "$(GREEN)✅ Development environment ready$(NC)"

clean: ## Clean generated files and directories
	@echo "$(BLUE)Cleaning up...$(NC)"
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf $(REPORTS_DIR)/*.html $(REPORTS_DIR)/*.xml $(REPORTS_DIR)/*.json
	rm -rf $(SCREENSHOTS_DIR)/*.png
	rm -rf $(LOGS_DIR)/*.log
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

# Testing Commands
test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	$(PYTEST) --html=$(REPORTS_DIR)/all-tests.html --self-contained-html --junitxml=$(REPORTS_DIR)/all-tests.xml
	@echo "$(GREEN)✅ All tests completed$(NC)"

test-smoke: ## Run smoke tests only
	@echo "$(BLUE)Running smoke tests...$(NC)"
	$(PYTEST) -m smoke --html=$(REPORTS_DIR)/smoke-tests.html --self-contained-html --junitxml=$(REPORTS_DIR)/smoke-tests.xml
	@echo "$(GREEN)✅ Smoke tests completed$(NC)"

test-api: ## Run API tests only
	@echo "$(BLUE)Running API tests...$(NC)"
	$(PYTEST) -m api --html=$(REPORTS_DIR)/api-tests.html --self-contained-html --junitxml=$(REPORTS_DIR)/api-tests.xml
	@echo "$(GREEN)✅ API tests completed$(NC)"

test-ui: ## Run UI tests only
	@echo "$(BLUE)Running UI tests...$(NC)"
	$(PYTEST) -m ui --html=$(REPORTS_DIR)/ui-tests.html --self-contained-html --junitxml=$(REPORTS_DIR)/ui-tests.xml
	@echo "$(GREEN)✅ UI tests completed$(NC)"

test-critical: ## Run critical tests only
	@echo "$(BLUE)Running critical tests...$(NC)"
	$(PYTEST) -m critical --html=$(REPORTS_DIR)/critical-tests.html --self-contained-html --junitxml=$(REPORTS_DIR)/critical-tests.xml
	@echo "$(GREEN)✅ Critical tests completed$(NC)"

test-performance: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	$(PYTEST) -m slow --html=$(REPORTS_DIR)/performance-tests.html --self-contained-html --junitxml=$(REPORTS_DIR)/performance-tests.xml
	@echo "$(GREEN)✅ Performance tests completed$(NC)"

test-parallel: ## Run tests in parallel
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	$(PYTEST) -n auto --html=$(REPORTS_DIR)/parallel-tests.html --self-contained-html --junitxml=$(REPORTS_DIR)/parallel-tests.xml
	@echo "$(GREEN)✅ Parallel tests completed$(NC)"

coverage: ## Run tests with coverage analysis
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTEST) --cov=telegram_bot_framework --cov-report=html:$(REPORTS_DIR)/coverage --cov-report=term-missing --cov-fail-under=80
	@echo "$(GREEN)✅ Coverage analysis completed$(NC)"
	@echo "$(BLUE)📊 Coverage report: $(REPORTS_DIR)/coverage/index.html$(NC)"

# Code Quality
format: ## Format code with Black
	@echo "$(BLUE)Formatting code...$(NC)"
	black . --check --diff || (echo "$(YELLOW)Formatting required. Running formatter...$(NC)" && black .)
	@echo "$(GREEN)✅ Code formatting completed$(NC)"

lint: ## Lint code with flake8
	@echo "$(BLUE)Linting code...$(NC)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "$(GREEN)✅ Linting completed$(NC)"

type-check: ## Type check with mypy
	@echo "$(BLUE)Type checking...$(NC)"
	mypy telegram_bot_framework.py --ignore-missing-imports || echo "$(YELLOW)⚠️  Type check warnings found$(NC)"
	@echo "$(GREEN)✅ Type checking completed$(NC)"

security-check: ## Security check with bandit
	@echo "$(BLUE)Running security checks...$(NC)"
	bandit -r . -f json -o $(REPORTS_DIR)/security-report.json || echo "$(YELLOW)⚠️  Security issues found$(NC)"
	safety check --json --output $(REPORTS_DIR)/safety-report.json || echo "$(YELLOW)⚠️  Dependency vulnerabilities found$(NC)"
	@echo "$(GREEN)✅ Security checks completed$(NC)"

quality-check: format lint type-check security-check ## Run all quality checks
	@echo "$(GREEN)✅ All quality checks completed$(NC)"

# Docker Commands
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	$(DOCKER) build -t $(IMAGE_NAME) .
	@echo "$(GREEN)✅ Docker image built: $(IMAGE_NAME)$(NC)"

docker-test: docker-build ## Run tests in Docker container
	@echo "$(BLUE)Running tests in Docker...$(NC)"
	$(DOCKER) run --rm \
		-e TELEGRAM_BOT_TOKEN \
		-e TELEGRAM_BOT_USERNAME \
		-e TELEGRAM_TEST_CHAT_ID \
		-e CI=true \
		-e HEADLESS=true \
		-v $(PWD)/$(REPORTS_DIR):/app/$(REPORTS_DIR) \
		-v $(PWD)/$(SCREENSHOTS_DIR):/app/$(SCREENSHOTS_DIR) \
		-v $(PWD)/$(LOGS_DIR):/app/$(LOGS_DIR) \
		$(IMAGE_NAME)
	@echo "$(GREEN)✅ Docker tests completed$(NC)"

docker-smoke: docker-build ## Run smoke tests in Docker
	@echo "$(BLUE)Running smoke tests in Docker...$(NC)"
	$(DOCKER) run --rm \
		-e TELEGRAM_BOT_TOKEN \
		-e TELEGRAM_BOT_USERNAME \
		-e TELEGRAM_TEST_CHAT_ID \
		-e CI=true \
		-v $(PWD)/$(REPORTS_DIR):/app/$(REPORTS_DIR) \
		$(IMAGE_NAME) \
		python -m pytest -m smoke --html=$(REPORTS_DIR)/docker-smoke-tests.html
	@echo "$(GREEN)✅ Docker smoke tests completed$(NC)"

docker-compose-test: ## Run tests with docker-compose
	@echo "$(BLUE)Running tests with docker-compose...$(NC)"
	$(DOCKER_COMPOSE) --profile testing up --build --abort-on-container-exit
	@echo "$(GREEN)✅ Docker Compose tests completed$(NC)"

docker-clean: ## Clean Docker images and containers
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	$(DOCKER) system prune -f
	$(DOCKER) image rm $(IMAGE_NAME) 2>/dev/null || true
	@echo "$(GREEN)✅ Docker cleanup completed$(NC)"

# Reporting and Documentation
reports: ## Generate consolidated test report
	@echo "$(BLUE)Generating consolidated report...$(NC)"
	$(PYTHON) scripts/generate_consolidated_report.py $(REPORTS_DIR)/
	@echo "$(GREEN)✅ Consolidated report generated$(NC)"

serve-docs: ## Serve documentation locally
	@echo "$(BLUE)Starting documentation server...$(NC)"
	@echo "$(YELLOW)📚 Documentation available at: http://localhost:8080$(NC)"
	$(DOCKER_COMPOSE) --profile docs up -d
	@echo "$(GREEN)✅ Documentation server started$(NC)"

stop-docs: ## Stop documentation server
	@echo "$(BLUE)Stopping documentation server...$(NC)"
	$(DOCKER_COMPOSE) --profile docs down
	@echo "$(GREEN)✅ Documentation server stopped$(NC)"

# CI/CD Commands
ci-setup: ## Setup for CI/CD environment
	@echo "$(BLUE)Setting up CI/CD environment...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@mkdir -p $(REPORTS_DIR) $(SCREENSHOTS_DIR) $(LOGS_DIR)
	@echo "$(GREEN)✅ CI/CD setup completed$(NC)"

ci-test: ## Run tests in CI/CD mode
	@echo "$(BLUE)Running CI/CD tests...$(NC)"
	CI=true HEADLESS=true $(PYTEST) \
		-m "smoke or critical" \
		--tb=short \
		--html=$(REPORTS_DIR)/ci-test-report.html \
		--self-contained-html \
		--junitxml=$(REPORTS_DIR)/ci-junit.xml \
		--cov=telegram_bot_framework \
		--cov-report=xml:$(REPORTS_DIR)/coverage.xml
	@echo "$(GREEN)✅ CI/CD tests completed$(NC)"

# Development Helpers
dev-shell: ## Start development shell in Docker
	@echo "$(BLUE)Starting development shell...$(NC)"
	$(DOCKER_COMPOSE) --profile dev run --rm dev-shell

check-env: ## Check environment variables
	@echo "$(BLUE)Checking environment variables...$(NC)"
	@if [ -z "$$TELEGRAM_BOT_TOKEN" ]; then echo "$(RED)❌ TELEGRAM_BOT_TOKEN not set$(NC)"; else echo "$(GREEN)✅ TELEGRAM_BOT_TOKEN set$(NC)"; fi
	@if [ -z "$$TELEGRAM_BOT_USERNAME" ]; then echo "$(RED)❌ TELEGRAM_BOT_USERNAME not set$(NC)"; else echo "$(GREEN)✅ TELEGRAM_BOT_USERNAME set$(NC)"; fi
	@if [ -z "$$TELEGRAM_TEST_CHAT_ID" ]; then echo "$(RED)❌ TELEGRAM_TEST_CHAT_ID not set$(NC)"; else echo "$(GREEN)✅ TELEGRAM_TEST_CHAT_ID set$(NC)"; fi

demo: ## Run a demo test suite
	@echo "$(BLUE)Running demo test suite...$(NC)"
	@echo "$(YELLOW)This will run a comprehensive demo of the framework$(NC)"
	$(PYTEST) -m "smoke or critical" -v --html=$(REPORTS_DIR)/demo-report.html --self-contained-html
	@echo "$(GREEN)✅ Demo completed! Check $(REPORTS_DIR)/demo-report.html$(NC)"

# Maintenance
update-deps: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✅ Dependencies updated$(NC)"

backup-results: ## Backup test results
	@echo "$(BLUE)Backing up test results...$(NC)"
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	tar -czf backup_$$timestamp.tar.gz $(REPORTS_DIR) $(SCREENSHOTS_DIR) $(LOGS_DIR); \
	echo "$(GREEN)✅ Backup created: backup_$$timestamp.tar.gz$(NC)"

# Quick shortcuts
smoke: test-smoke ## Shortcut for smoke tests
api: test-api ## Shortcut for API tests
ui: test-ui ## Shortcut for UI tests
all: test ## Shortcut for all tests