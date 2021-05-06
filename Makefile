# Makefile for Python ADSB Cursor-on-Target Gateway.
#
# Source:: https://github.com/ampledata/stratuxcot
# Author:: Greg Albrecht W2GMD <oss@undef.net>
# Copyright:: Copyright 2020 Orion Labs, Inc.
# License:: Apache License, Version 2.0
#


.DEFAULT_GOAL := all


all: develop

install_requirements_test:
		pip install -r requirements_test.txt

develop:
	python setup.py develop

install:
	python setup.py install

uninstall:
	pip uninstall -y stratuxcot

reinstall: uninstall install

clean:
	@rm -rf *.egg* build dist *.py[oc] */*.py[co] cover doctest_pypi.cfg \
		nosetests.xml pylint.log output.xml flake8.log tests.log \
		test-result.xml htmlcov fab.log .coverage */__pycache__

publish:
	python setup.py register sdist upload


pep8: remember_test
	flake8 --max-complexity 12 --exit-zero *.py stratuxcot/*.py

flake8: pep8

lint: remember_test
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
		-r n *.py stratuxcot/*.py || exit 0

pylint: lint

test: lint pep8 pytest

checkmetadata:
	python setup.py check -s --restructuredtext
