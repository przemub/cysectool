### v1.1 - 19th of November, 2020
State before the meeting with Pasquale before the meeting with NCSC.

* New model, ClearSCADA, added. Edges and attacks based on the document supplied by NCSC while controls are mostly based on the last year's case study.
* Multiprocessing added to the Pareto frontier generation, dividing its generation time roughly by the number of cores.
* Editor changes. Styling, View button, selection of vertices from the menu instead of by ID, graph title input.
* Visualiser requests a refresh when it losts connection (i.e. due to a server restart).
* Unit tests added for the main optimisation routine and some model methods.
* Selenium tests added for the GUI. Notably, they exclude Bokeh drawing and, for the time being, the Pareto frontier.
* Tests run automatically on GitHub after each commit. macOS tests can be trigerred manually.
* Updated to Bokeh 2.0 series and PuLP 2.3 series. Minor dependencies updated to the latest versions.

### v1.0 - 16th of November, 2019

State of the project as after finishing my employment at QMUL.
All basic stuff envisioned in the project was added - model editor,
model auto-drawing, performing optimisation, showing a Pareto frontier.
