DOCHOST ?= $(shell bash -c 'read -p "documentation host: " dochost; echo $$dochost')

# dynamic unittest_01 VERSION detection (via version str in pyproject.toml)
#
# - at this point, I prefer printing in perl to set shell variables...
#   - open './pyproject.toml' as $pyproject
#   - loop over each line, assigned to $line
#   - If we see the version string in a line, print it and end
export VERSION := $(shell perl -e 'open my $$pyproject, "pyproject.toml"; while (my $$line = <$$pyproject>) { if ( $$line =~ s/version.+?(\d+.\d+.\d+)\D\s*/$$1/g ) { print "$$line"; exit 0; } }' )


# We must escape Makefile dollar signs as $$foo...
export PING_STATUS := $(shell perl -e '@output = qx/ping -q -W0.5 -c1 4.2.2.2/; $$alloutput = join "", @output; if ( $$alloutput =~ /\s0\sreceived/ ) { print "failure"; } else { print "success"; }')

export NUMBER_OF_CCP_TESTS := $(shell grep "def " tests/test*py | wc -l)

# Makefile color codes...
#     ref -> https://stackoverflow.com/a/5947802/667301
COL_GREEN=\033[0;32m
COL_CYAN=\033[0;36m
COL_YELLOW=\033[0;33m
COL_RED=\033[0;31m
COL_END=\033[0;0m

.DEFAULT_GOAL := test


.PHONY: repo-push
repo-push:
	@echo "$(COL_GREEN)>> git push and merge (w/o force) to unittest_01 main branch to github$(COL_END)"
	make ping
	-git checkout master || git checkout main # Add dash to ignore checkout fails
	# Now the main branch is checked out...
	THIS_BRANCH=$(shell git branch --show-current)  # assign 'main' to $THIS_BRANCH
	git merge @{-1}                           # merge the previous branch into main...
	git push origin $(THIS_BRANCH)            # git push to origin / $THIS_BRANCH
	git checkout @{-1}                        # checkout the previous branch...


.PHONY: repo-push-force
repo-push-force:
	@echo "$(COL_GREEN)>> git push and merge (w/ force) unittest_01 local main branch to github$(COL_END)"
	make ping
	-git checkout master || git checkout main # Add dash to ignore checkout fails
	# Now the main branch is checked out...
	THIS_BRANCH=$(shell git branch --show-current)  # assign 'main' to $THIS_BRANCH
	git merge @{-1}                           # merge the previous branch into main...
	git push --force-with-lease origin $(THIS_BRANCH)    # force push to origin / $THIS_BRANCH
	git checkout @{-1}                        # checkout the previous branch...

.PHONY: repo-push-tag
repo-push-tag:
	@echo "$(COL_GREEN)>> git push (w/ local tag) unittest_01 local main branch to github$(COL_END)"
	git push origin +main
	git push --tags origin +main

.PHONY: repo-push-tag-force
repo-push-tag-force:
	@echo "$(COL_GREEN)>> git push (w/ local tag and w/ force) unittest_01 local main branch to github$(COL_END)"
	git push --force-with-lease origin +main
	git push --force-with-lease --tags origin +main

.PHONY: pylama
pylama:
	@echo "$(COL_GREEN)>> running pylama against unittest_01$(COL_END)"
	# Good usability info here -> https://pythonspeed.com/articles/pylint/
	pylama --ignore=E501,E301,E265,E266 unittest_01/*py | less -XR

.PHONY: pylint
pylint:
	@echo "$(COL_GREEN)>> running pylint against unittest_01$(COL_END)"
	# Good usability info here -> https://pythonspeed.com/articles/pylint/
	pylint --rcfile=./utils/pylintrc --ignore-patterns='^build|^dist|utils/pylintrc|README.rst|CHANGES|LICENSE|MANIFEST.in|Makefile|TODO' --output-format=colorized * | less -XR

.PHONY: flake
flake:
	flake8 --ignore E501,E226,E225,E221,E303,E302,E265,E128,E125,E124,E41,W291 --max-complexity 10 unittest_01 | less

.PHONY: ruff
ruff:
	pip install -U ruff
	ruff check --no-cache --ignore E501,E226,E225,E221,E265,W291 *py
	ruff check --no-cache --ignore E501,E226,E225,E221,E265,W291 my_module/*py
	ruff check --no-cache --ignore E501,E226,E225,E221,E265,W291 tests/*py

.PHONY: coverage
coverage:
	@echo "[[[ py.test Coverage ]]]"
	cd tests;py.test --cov-report term-missing --cov=unittest_01.py -s -v

.PHONY: pydocstyle
pydocstyle:
	# Run a numpy-style doc checker against all files matching unittest_01/*py
	find unittest_01/*py | xargs -I{} pydocstyle --convention=numpy {}

.PHONY: rm-timestamp
rm-timestamp:
	@echo "$(COL_GREEN)>> delete .pip_dependency if older than a day$(COL_END)"
	#delete .pip_dependency if older than a day
	$(shell find .pip_dependency -mtime +1 -exec rm {} \;)

.PHONY: timestamp
timestamp:
	@echo "$(COL_GREEN)>> Create .pip_dependency$(COL_END)"
	$(shell touch .pip_dependency)

.PHONY: ping
ping:
	@echo "$(COL_GREEN)>> ping to ensure internet connectivity$(COL_END)"
	@if [ "$${PING_STATUS}" = 'success' ]; then return 0; else return 1; fi

.PHONY: test
test:
	@echo "$(COL_GREEN)>> running unit tests$(COL_END)"
	$(shell touch .pip_dependency)
	make timestamp
	make clean
	# Attempt to fix strange github unit test import failures
	cd tests && pytest -sxvvvvvvvvvv

.PHONY: clean
clean:
	@echo "$(COL_GREEN)>> cleaning the repo$(COL_END)"
	# Delete bogus files... see https://stackoverflow.com/a/73992288/667301
	perl -e 'unlink( grep { /^=\d*\.*\d*/ && !-d } glob( "*" ) );'
	find ./* -name '*.pyc' -exec rm {} \;
	find ./* -name '*.so' -exec rm {} \;
	find ./* -name '*.coverage' -exec rm {} \;
	find ./* -name '*.cover' -exec rm {} \;
	@# A minus sign prefixing the line means it ignores the return value
	-find ./* -path '*__pycache__' -exec rm -rf {} \;
	-rm .pip_dependency
	-rm -rf .mypy_cache/
	-rm -rf poetry.lock
	-rm -rf .pytest_cache/
	-rm -rf .eggs/
	-rm -rf .cache/
	-rm -rf build/ dist/ unittest_01.egg-info/ setuptools*

