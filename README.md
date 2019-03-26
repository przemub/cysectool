## Requirements
* Python 3.6+
* virtualenv & pip OR conda

## virtualenv way
### Setup
```sh
git clone https://github.com/przemub/security-graph-visualiser
cd security-graph-visualiser
virtualenv3 venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run
```sh
source venv/bin/activate
python -m bokeh serve visualiser
```

## conda way
### Setup
```sh
git clone https://github.com/przemub/security-graph-visualiser
cd security-graph-visualiser
conda env create -f environment.yml
```

### Run
```sh
conda activate visualiser
python -m bokeh serve visualiser --show
```

