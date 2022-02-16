## Requirements
* Python 3.7+
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

## Test
Once you have a working environment:
```sh
python -m unittest
```

For testing the optimization routine, see `test/test_model.py`. The way to test a model is to subclass `TemplateTestCase` (when testing a built-in model) or `FixtureTestCase` (when testing an extra model used only for testing). In the first case, set `model_number` to the number of the model. In the latter, put the model in `doc/fixtures` folder and set `fixture_name` to the name of the model (without extension).

Afterwards, take a look at `CustomAdjustmentTestCase` to see the parameters that can be tested and set them in your test case.

For testing the GUI, see `test/test_gui.py`. These tests are run using headless Firefox and Chromium browsers instrumented by Selenium framework. Refer to [Selenium with Python](https://selenium-python.readthedocs.io/) docs in order to learn how to use it.

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
* tests - see [Tests](#Tests)
* doc - all kinds of research output and analysis tools
    * **doc/templates - graph templates used in the application** (probably should be moved)
    * doc/fixtures - graph templates used for automated testing
