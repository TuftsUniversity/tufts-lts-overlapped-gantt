**Compressed Gantt For Project Management**

**Purpose:**

The purpose of this script is to help you plan your projects for the year by expanding the idea of the Gantt chart such that projects are “nested” and “tiled”, i.e. not all on separate lines so that you can see how much demand you will have at a given time

**Input:**

To accomplish this, the input sheet should have projects described by the following fields:

- “task”
  - This is really the project
  - Given level of effort below, you may want to break up projects that have different segments with different levels of effort at different times, but keeping in mind that this is a generalization
- start_date
  - must be in YYYY-MM-DD in text format
- end_date
  - must be in YYYY-MM-DD in text format
- level_of_effort
  - level of effort at a given time, roughly corresponding to hours per day
  - this is an estimate and average

**Method:**

To use this script first install the requirements using the following line

python3 -m pip install -r requirements.txt

Then you can run the program with python3 continuousGantt.py

**Output:**

it opens a matplotlib interactive window with this broken bar chart. You can save and export from here.

A use of this would then be to go back to your input spreadsheet and adjust dates so there isn’t too much demand at one time or overlap