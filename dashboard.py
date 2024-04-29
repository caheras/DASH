import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import pymongo

# Set up MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["COVID"]  # Replace with your database name
collection = db["covid-data"]  # Replace with your collection name
collection.create_index([("continent", pymongo.ASCENDING)])
collection.create_index([("date", pymongo.ASCENDING)])

def get_top_countries_by_total_cases():
    pipeline = [
        {"$group": {
            "_id": "$location",
            "total_cases": {"$last": "$total_cases"}
        }},
        {"$sort": {"total_cases": -1}},
        {"$limit": 10}
    ]
    return list(collection.aggregate(pipeline))

# Call the function and create the DataFrame
top_countries_data = get_top_countries_by_total_cases()
top_countries_df = pd.DataFrame(top_countries_data)
top_countries_df.rename(columns={'_id': 'country', 'total_cases': 'total_cases'}, inplace=True)

# Create the figure for the static graph
top_countries_fig = px.bar(top_countries_df, x='country', y='total_cases', title='Top 10 Countries by Total Cases')
top_countries_fig.update_layout(
    paper_bgcolor='rgba(51,51,51,1)',  # Sets the outer background color to dark gray
    plot_bgcolor='rgba(51,51,51,1)',   # Sets the inner plot background color to dark gray
    font=dict(color='white')  # Sets the color of the tick labels to white
)

def get_life_expectancy_by_continent():
    pipeline = [
        {"$match": {"continent": {"$ne": None}, "life_expectancy": {"$gte": 0}}},  # Exclude documents with null continent or negative life expectancy
        {"$group": {
            "_id": "$continent",
            "average_life_expectancy": {"$avg": "$life_expectancy"}
        }},
        {"$sort": {"average_life_expectancy": -1}}  # Sort by average life expectancy in descending order
    ]
    return list(collection.aggregate(pipeline))


# Fetch the data once when the server starts
life_expectancy_data = get_life_expectancy_by_continent()
life_expectancy_df = pd.DataFrame(life_expectancy_data)
life_expectancy_df.rename(columns={'_id': 'continent', 'average_life_expectancy': 'average_life_expectancy'}, inplace=True)

# Create the figure for the static bar chart
life_expectancy_fig = px.bar(life_expectancy_df, x='continent', y='average_life_expectancy', title='Average Life Expectancy by Continent')
life_expectancy_fig.update_layout(
    paper_bgcolor='rgba(51,51,51,1)',  # Sets the outer background color to dark gray
    plot_bgcolor='rgba(51,51,51,1)',   # Sets the inner plot background color to dark gray
    font=dict(color='white')  # Sets the color of the tick labels to white
)


# Query MongoDB to get distinct continents
try:
    continent_options = collection.distinct('continent')
    # Filter out any non-string values from the list
    continent_options = [str(continent) for continent in continent_options if continent is not None]
except Exception as e:
    print(f"An error occurred when retrieving continents: {e}")
    continent_options = []

# Ensure the default value 'All Continents' is included
if 'All Continents' not in continent_options:
    continent_options.insert(0, 'All Continents')

# Filter out the 'NaN' string if the NaN values have been converted to string
valid_continent_options = [option for option in continent_options if option != 'nan']

# Now create your dropdown options
dropdown_options = [{'label': continent, 'value': continent} for continent in valid_continent_options]


# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Define your app layout with combined elements and styling
app.layout = html.Div([
    html.H1('COVID-19 Data Dashboard', id='title', style={'textAlign': 'center', 'marginTop': '20px'}),
    dbc.Container([  # Use a container to add padding and center your layout
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        dcc.Graph(id='graph-total-cases'),
                        dcc.Dropdown(
                            id='dropdown-continent',
                            options= dropdown_options,
                            value='All Continents',
                            style={'color': '#212121'}  # Dropdown text color
                        ),
                        # ... other interactive components ...
                    ]),
                    className='mb-3',  # Margin bottom
                    color='rgba(51,51,51,1)',  # Set the card color to dark
                ),
                width=12,  # Set the column width to use the whole width of the container
            )
        ),
    ], fluid=True),  # Container fluid ensures that it uses the full width available
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        dcc.Graph(id='graph-total-deaths'),
                        dcc.Dropdown(
                            id='dropdown-continent-deaths',
                            options=dropdown_options,
                            value='All Continents'
                        ),
                    ]),
                    className='mb-3',
                    color='rgba(51,51,51,1)',  # Set the card color to dark
                ),
                width={'size': 10, 'offset': 1},  # Center the card on the page
            )
        ),
        # Inside your dbc.Container, add another dbc.Row for the new graph
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        dcc.Graph(id='graph-people-vaccinated'),
                        dcc.Dropdown(
                            id='dropdown-continent-vaccinated',
                            options=dropdown_options,
                            value='All Continents'
                        ),
                    ]),
                    className='mb-3',
                    color='rgba(51,51,51,1)',  # Set the card color to dark
                ),
            )
        ),
        # Inside your dbc.Container, add another dbc.Row for the new static graph
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        dcc.Graph(id='graph-top-countries-total-cases', figure=top_countries_fig),
                        # You do not need a dropdown since this is a static graph
                    ]),
                    color='rgba(51,51,51,1)',  # Set the card color to dark
                    className='mb-3',
                ),
            )
        ),
        dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id='graph-case-distribution', figure=life_expectancy_fig),
                ]),
                color='rgba(51,51,51,1)',  # Set the card color to dark
                className='mb-3',
                ),
            )
        ),
# ... existing layout for other graphs ...
])

def get_aggregated_data(selected_continent):
    pipeline = [
        {"$match": {"continent": selected_continent} if selected_continent != 'All Continents' else {}},
        {"$group": {
            "_id": {"date": "$date", "location": "$location"},
            "total_cases": {"$sum": "$new_cases"}  # Adjusted to the correct field name
        }},
        {"$sort": {"_id.date": 1}}
    ]
    return list(collection.aggregate(pipeline))

def get_latest_total_deaths_by_continent(continent):
    if continent and continent != 'All Continents':
        match_stage = {"$match": {"continent": continent}}
    else:
        match_stage = {"$match": {}}

    pipeline = [
        match_stage,
        # Sort by date in descending order to get the latest entry first
        {"$sort": {"date": -1}},
        # Group by location to get one document per country
        {"$group": {
            "_id": "$location",
            "latest_total_deaths": {"$first": "$total_deaths"}
        }},
        {"$sort": {"_id": 1}}  # Sort by country name in ascending order
    ]
    return list(collection.aggregate(pipeline))

def get_people_vaccinated_data(continent):
    if continent and continent != 'All Continents':
        match_stage = {"$match": {"continent": continent, "people_vaccinated": {"$exists": True}}}
    else:
        match_stage = {"$match": {"people_vaccinated": {"$exists": True}}}

    pipeline = [
        match_stage,
        {"$group": {
            "_id": {"date": "$date", "location": "$location"},
            "people_vaccinated": {"$last": "$people_vaccinated"}
        }},
        {"$sort": {"_id.date": 1}}  # Sort by date in ascending order
    ]
    return list(collection.aggregate(pipeline))

@app.callback(
    Output('graph-total-cases', 'figure'),
    [Input('dropdown-continent', 'value')]
)
def update_total_cases_graph(selected_continent):
    data = get_aggregated_data(selected_continent)
    df = pd.DataFrame(data)
    
    # Assuming the aggregated total cases are stored under 'total_cases'
    df['date'] = pd.to_datetime(df['_id'].apply(lambda x: x['date']))
    df['location'] = df['_id'].apply(lambda x: x['location'])
    
    # Here you should use 'total_cases', not 'all_cases'
    df['total_cases'] = pd.to_numeric(df['total_cases'])
    
    df.drop(columns=['_id'], inplace=True)
    df.sort_values('date', inplace=True)

    fig = px.line(df, x='date', y='total_cases', color='location', title='Total COVID-19 Cases Over Time')
    
    fig.update_traces(line=dict(width=2))

    fig.update_layout(
        paper_bgcolor='rgba(51,51,51,1)',  # Sets the outer background color to dark gray
        plot_bgcolor='rgba(51,51,51,1)',   # Sets the inner plot background color to dark gray
        font=dict(
            color='white'  # Sets the color of the tick labels to white
        )
    )
    return fig

@app.callback(
    Output('graph-total-deaths', 'figure'),
    [Input('dropdown-continent-deaths', 'value')]
)
def update_total_deaths_graph(selected_continent):
    data = get_latest_total_deaths_by_continent(selected_continent)
    df = pd.DataFrame(data)

    # Rename '_id' to 'country' for clarity in the graph
    df.rename(columns={'_id': 'country', 'latest_total_deaths': 'total_deaths'}, inplace=True)

    fig = px.bar(df, x='country', y='total_deaths', title='Latest Total Deaths by Country')

    # Update the layout as you did before
    fig.update_layout(
        paper_bgcolor='rgba(51,51,51,1)',  # Sets the outer background color to dark gray
        plot_bgcolor='rgba(51,51,51,1)',   # Sets the inner plot background color to dark gray
        font=dict(
            color='white'  # Sets the color of the tick labels to white
        )
    )

    return fig

@app.callback(
    Output('graph-people-vaccinated', 'figure'),
    [Input('dropdown-continent-vaccinated', 'value')]
)
def update_people_vaccinated_graph(selected_continent):
    data = get_people_vaccinated_data(selected_continent)
    df = pd.DataFrame(data)

    # Unpack the '_id' field to 'date' and 'location'
    df['date'] = pd.to_datetime(df['_id'].apply(lambda x: x['date']))
    df['location'] = df['_id'].apply(lambda x: x['location'])
    df.drop(columns=['_id'], inplace=True)
    
    # Sort the data for better plotting (if not already sorted in the pipeline)
    df.sort_values(by=['location', 'date'], inplace=True)

    fig = px.line(df, x='date', y='people_vaccinated', color='location',
                  title='People Vaccinated Over Time')

    # Update layout with dark theme styles as before
    fig.update_layout(
        paper_bgcolor='rgba(51,51,51,1)',  # Sets the outer background color to dark gray
        plot_bgcolor='rgba(51,51,51,1)',   # Sets the inner plot background color to dark gray
        font=dict(
            color='white'  # Sets the color of the tick labels to white
        )
    )

    return fig


# Create the figure for the static graph
# ... other callbacks for additional graphs and interactive components ...

if __name__ == '__main__':
    app.run_server(debug=True)
