
all: install run

create-venv:
	if [ ! -d "venv" ]; then python3 -m venv venv; fi

install: create-venv
	source ./venv/bin/activate; python3 -m pip install -r requirements.txt; deactivate

install-test: create-venv
	source ./venv/bin/activate; python3 -m pip install -r requirements.txt; python3 -m pip install -r test_requirements.txt; deactivate

run:
	source ./venv/bin/activate; uvicorn main:app; deactivate

test: install-test
	-rm iot_test.db
	source ./venv/bin/activate; python3 -m pytest; deactivate

cover: install-test
	-rm iot_test.db
	source ./venv/bin/activate; python3 -m pytest --cov; deactivate

clean:
	rm -rf ./venv
	rm -f *test.db
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -r .coverage

clean-db:
	rm -f *test.db
	rm -f *.db
