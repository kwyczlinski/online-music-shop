# Online-Music-Shop

## Author:

name: Krzysztof

surname: Wyczlinski

group: II

# How to start the app

## Start venv & install libraries:

python3 -m venv .venv

. .venv/bin/activate

pip install -r requirements.txt

## How to execute tests

#### Only unit:

python3 -m pytest -m "not integration"

Run unit and integration (Geoapify won't start without key): \
python3 -m pytest

#### BDD API & performance tests

Before tests start flask server: \
export PYTHONPATH=$PWD
python3 app/run.py &

Run BDD API tests: \
behave

Run performance tests: \
python3 -m pytest tests/perf/test_performance.py

## How to check coverage (API is tested through http hence no coverage)

python3 -m coverage run --source=src -m pytest

Show report: \
python3 -m coverage report \
Generate html report: \
python3 -m coverage html
