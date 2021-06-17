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


.PHONY: help
help: ## Show this help information
	@printf "\e[32m====================\n  TeSLA CE v%s\n====================\n" $(VERSION)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

package: ## Build Python package wheel
	@echo "build package"
docker: package ## Build Docker image
	@echo "build docker"
build: package docker ## Build all targets
	@echo "build all"

