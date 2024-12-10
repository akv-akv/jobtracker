.PHONY: run clean

VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

venv-dev: clean
	@echo "Creating a new virtual environment..."
	python3 -m venv $(VENV)
	$(PIP) install -r requirements/dev.txt
	touch $(VENV)/bin/activate
	@echo "Virtual environment rejuvenated."

clean:
	rm -rf __pycache__
	rm -rf $(VENV)
