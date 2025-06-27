
all: install run

create-venv:
	if [ ! -d "venv" ]; then python3 -m venv venv; fi

install: create-venv
	. ./venv/bin/activate && python3 -m pip install -r requirements.txt

install-test: create-venv
	. ./venv/bin/activate && python3 -m pip install -r requirements.txt && python3 -m pip install -r test_requirements.txt

run:
	. ./venv/bin/activate && uvicorn main:app

test: install-test
	-rm iot_test.db
	. ./venv/bin/activate && python3 -m pytest

cover: install-test
	-rm iot_test.db
	. ./venv/bin/activate && python3 -m pytest --cov

clean:
	rm -rf ./venv
	rm -f *test.db
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -f .coverage

clean-db:
	rm -f *test.db
	rm -f *.db
