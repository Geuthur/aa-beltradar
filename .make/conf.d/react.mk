# Makefile fragment for React-related tasks

# React Test Build
.PHONY: react-test-build
react-test-build: check-python-venv check-myauth-path
	@echo "Running React test build"
	@cd $(REACT__EXECUTABLE) && $(REACT__TEST_BUILD_SCRIPT)
	@echo "React test build completed"

# React Release Build
.PHONY: react-release
react-release: check-python-venv check-myauth-path
	@echo "Running React release build"
	@cd $(REACT__EXECUTABLE) && $(REACT__RELEASE_BUILD_SCRIPT)
	@echo "React release build completed"

.PHONY: react-openapi
react-openapi: check-python-venv check-myauth-path
	@echo "Starting React OpenAPI migration"
	@read -p "Are you sure you want to proceed with the React OpenAPI migration? (y/N) " confirm && [ "$$confirm" = "y" ]
	@cd $(REACT__EXECUTABLE) && $(REACT__OPENAPI_SCRIPT)
	@echo "React OpenAPI migration completed"

.PHONY: react-eslint
react-eslint: check-python-venv check-myauth-path
	@echo "Running React ESLint check"
	@cd $(REACT__EXECUTABLE) && npx eslint . --fix
	@echo "React ESLint check completed"

# Help Message
.PHONY: help
help::
	@echo "  $(TEXT_UNDERLINE)React:$(TEXT_UNDERLINE_END)"
	@echo "    react-test-build   Run the React test build"
	@echo "    react-release      Run the React release build"
	@echo "    react-openapi      Migrate OpenAPI to React"
	@echo "    react-eslint       Run the React ESLint check"
	@echo ""
