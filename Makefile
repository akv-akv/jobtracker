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

alembic-upgrade:
	@echo "Running alembic upgrade..."
	POSTGRES_USER=postgres \
	POSTGRES_PASSWORD=postgres \
	POSTGRES_HOSTNAME=localhost \
	APPLICATION_DB=jobtracker \
	$(VENV)/bin/alembic upgrade head

alembic-autogenerate:
	@echo "Running alembic autogenerate..."
	POSTGRES_USER=postgres \
	POSTGRES_PASSWORD=postgres \
	POSTGRES_HOSTNAME=localhost \
	APPLICATION_DB=jobtracker \
	$(VENV)/bin/alembic revision --autogenerate -m "Initial"

alembic-downgrade:
	@echo "Running alembic autogenerate..."
	POSTGRES_USER=postgres \
	POSTGRES_PASSWORD=postgres \
	POSTGRES_HOSTNAME=localhost \
	APPLICATION_DB=jobtracker \
	$(VENV)/bin/alembic downgrade -1
