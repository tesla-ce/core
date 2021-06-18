#  Copyright (c) 2021 Xavier Baro
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
VERSION = `cat src/tesla_ce/lib/data/VERSION`

# Uncomment to use PosgreSQL
# DATABASE = "postgres"

ifneq "$(wildcard .venv )" ".venv"
  # if virtual environment exists:
  REQUIREMENT = .venv 
else
  # if it doesn't:
  REQUIREMENT =
endif

ifneq "$(wildcard .venv/bin/tesla_ce )" ".venv/bin/tesla_ce"
  # if TeSLA CE command exists:
  INVALID_VENV = error_msg
else
  # if it doesn't:
  INVALID_VENV =
endif

DB_REQUIREMENTS = mysqlclient
ifdef DATABASE
  DB_REQUIREMENTS = psycopg2
endif

.DELETE_ON_ERROR: .venv

db_check:
	@printf "Database requirements: [%s]\n" $(DB_REQUIREMENTS)

check_venv:
        @printf "ENV CHECK Database requirements: [%s]\n" $(DB_REQUIREMENTS)


.PHONY: help
help: ## Show this help information
	@printf "\e[32m====================\n  TeSLA CE v%s\n====================\n" $(VERSION)
	@printf "\n\033[0mMySQL is used as default database. Use \033[36m-e DATABASE=postresql\033[0m option to select PostgreSQL.\n\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.venv: db_check ## Create a Python virtual environment and install required packages
	python3 -m venv .venv
	rm -f requirements.txt
	.venv/bin/python -m pip install pip --upgrade
	@printf ".venv/bin/pip install %s\n" $(DB_REQUIREMENTS)
	.venv/bin/pip install $(DB_REQUIREMENTS) || (rm -Rf .venv && error "Missing database client")
	.venv/bin/pip install pip-tools
	sed -i "s/mysqlclient/# mysqlclient/g" requirements.in
	sed -i "s/psycopg2/# psycopg2/g" requirements.in
	.venv/bin/pip-compile
	.venv/bin/pip install -r requirements.txt || (rm -Rf .venv && error "Failed installing TeSLA CE dependences")

.PHONY: python_venv
python_venv: $(REQUIREMENT) check_venv ## Create a Python virtual environment and install required packages
	@echo "Virtual Environment ready"
	@.venv/bin/python --version

.PHONY: package
package: python_venv ## Build Python package wheel
	@echo "build package"

.PHONY: docker
docker: package ## Build Docker image
	@echo "build docker"

.PHONY: build
build: package docker ## Build all targets
	@echo "build all"

.PHONY: clean
clean:  ## Clean all environment
	rm -Rf .venv
	rm -f requirements.txt


