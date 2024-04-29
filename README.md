# COVID-19 Dashboard

The COVID-19 Dashboard is an interactive web application designed to visualize various statistics related to the COVID-19 pandemic. It leverages a MongoDB database to store the data and uses a Python Dash application for the web interface.

## Features

- Visualization of COVID-19 data across different continents and countries.
- Multiple graphs displaying total cases, deaths, and vaccination statistics over time.
- Ability to filter data by continent.
- Static graphs showing overall data like total cases and average life expectancy.

## Services Used

- MongoDB for database management.
- Python Dash for creating the interactive dashboard.
- Plotly for generating the graphs.
- Pandas for data manipulation and analysis.

## Requirements

To run the COVID-19 Dashboard on your local machine, you will need:

- Python 3.x
- MongoDB installed and running on `localhost:27017`
- The following Python packages:
  - dash
  - dash-bootstrap-components
  - plotly
  - pandas
  - pymongo

You can install the necessary Python packages with the following command:

```bash
pip install dash dash-bootstrap-components plotly pandas pymongo
```
## Configuration

- First run the backend.py script to install the database locally on your machine (Do not panic if it looks stuck, be patient)
- Run the dashboard.py script to deploy the dashboard (be patient, it may take a bit to load)
- Click on the link that appears on the terminal and the dashboard should appear on your browser of choice
