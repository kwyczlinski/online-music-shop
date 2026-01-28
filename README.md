# Online-Music-Shop

## Author:

name: Krzysztof

surname: Wyczlinski

group: II

# How to start the app

## Start venv & install libraries:

python3 -m venv .venv

. .venv/bin/activate

pip install -r

## How to execute tests

Only unit: \
python3 -m pytest -m "not integration"

Run all: \
python3 -m pytest

## How to check coverage

python3 -m coverage run --source=src -m pytest

Show report: \
python3 -m coverage report \
Generate html report: \
python3 -m coverage html
