.PHONY: test validate

test:
	python -m unittest discover -s tests -p 'test_*.py' -v

validate:
	python tools/qso_validate.py examples/minimal/minimal.qso.json
