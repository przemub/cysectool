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
python main.py
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
conda activate visualiser-env
python main.py
```

# Structure

* main.py - Bokeh server runner
* src - Python server-side source code
    * visualiser.py - analyzer/visualiser application code
        * drawing.py - graph drawing routines
        * api.py - API routes
    * data.py - attack graph data structures
        * optimization.py - optimization routines
    * edit.py - graph editor application code (see my_static/js/edit.js)
* my_static/js - JavaScript client-side code
    * edit.js - graph editor code
    * main.js - some fix-ups to Bokeh
    * callbacks.js - events handling
* templates - HTML templates of the sites, written in [Jinja2](https://jinja.palletsprojects.com/en/2.10.x/)
* doc - all kinds of research output and analysis tools
    * **doc/templates - graph templates used in the application** (probably should be moved)
