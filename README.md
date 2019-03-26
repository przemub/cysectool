## Requirements
* Python 3.5+
* virtualenv
* pip

## Setup
```sh
git clone https://github.com/przemub/security-graph-visualiser
cd security-graph-visualiser
virtualenv3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run
```sh
source venv/bin/activate
python -m bokeh serve visualiser
```
