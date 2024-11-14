# app.py

import dash
from dash import dcc, html, Input, Output, State
import new  # Import the new.py script to call generate_report3 function
import importlib

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout for the Dash app
app.layout = html.Div(
    style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'height': '100vh',
        'textAlign': 'center',
    },
    children=[
        html.H1("Dynamic Chart Generator", style={'textAlign': 'center'}),
        html.P("Enter a description to dynamically generate a chart.", style={'textAlign': 'center'}),
        
        # Centered input and button
        html.Div(
            style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'},
            children=[
                dcc.Input(id="description-input", type="text", placeholder="Enter description"),
                html.Button("Generate Chart", id="generate-button", n_clicks=0),
            ]
        ),
        
        # Placeholder for generated chart
        dcc.Graph(id='employment-status-chart'),
        
        # Placeholder for success message
        html.Div(id="output-message", style={'marginTop': '20px', 'textAlign': 'center'})
    ]
)

# Callback to handle chart generation and display it on the same page
@app.callback(
    [Output("employment-status-chart", "figure"), Output("output-message", "children")],
    Input("generate-button", "n_clicks"),
    State("description-input", "value")
)
def generate_and_display_chart(n_clicks, description):
    if n_clicks > 0 and description:
        # Generate the code in graph_code.py based on the description
        new.generate_report3(description)
    return {}, ""

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
