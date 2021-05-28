init:
	pip install -r requirements_dev.txt

test:
	python -m unittest discover -s 'tests' -p 'test*.py' -v

doc:
	# sphinx-apidoc --module-first -f -o docs/source pandas_x
	make -C docs/ clean
	make -C docs/ html

# EXAMPLE TASKS FOR FUTURE

clean:
	rm -Rf *.egg-info build dist

testpublish:
	# git push origin && git push --tags origin
	$(MAKE) clean
	# pip install --quiet twine wheel
	# pip install twine wheel
	# python setup.py bdist_wheel
	python setup.py sdist bdist_wheel
	twine check dist/*
	# twine upload -r testpypi dist/*
	# $(MAKE) clean

# clean-pyc:
#   find . -name '*.pyc' -exec rm --force {} +
#   find . -name '*.pyo' -exec rm --force {} +
#   name '*~' -exec rm --force  {}

# isort:
#   sh -c "isort --skip-glob=.tox --recursive . "

# lint:
#   flake8 --exclude=.tox
