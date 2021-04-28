### v1.2 - 29th of April, 2021
The release made before submitting the final version of the report, on which all the data, graphs, and conclusions in the paper are based. It is also the release used during the viva and preparation for it.

* Seven more iterations of ClearSCADA model are added. The final, eighth "try" represents the state of the model as described in the report. The differences between iterations can be used to show how a model can be developed.
* A simple greedy algorithm to find the critical path (the most probable attack vector) and mark it with a thicker line was added.
* The ability to set a different impact of a control group on each edge was reworked. Now, for each vulnerability, either the default impact for all controls in the group is used, or one can specify impacts for each control in the group.
* Add an ability to associate an URL with a vulnerability, which will be opened when a corresponding edge is clicked.
* Adapt the Dockerfile for ARM64 and ppc64le compatibility.
* Add an ability to set the default targets in the editor.
* Saving and loading bugfixes.
* Improve error reporting.
* When running Python in non-debugging mode, most debugging messages are silenced.

### v1.1 - 19th of October, 2020
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
