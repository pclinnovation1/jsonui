import pandas as pd
import base64
import io
from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.express as px
import plotly.graph_objects as go

# Initialize the Dash app
app = Dash(__name__)
app.config.suppress_callback_exceptions = True

# Helper function to parse uploaded files
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return html.Div(['There was an error processing this file.'])
    except Exception as e:
        return html.Div(['There was an error processing this file.'])
    return df, filename

# App layout
app.layout = html.Div([
    html.H1("Data Visualization Tool"),

    # File upload
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    ),
    html.Div(id='output-file-upload'),

    # Layout adjustment
    html.Div([
        html.Div([
            html.H2("Fields"),
            dcc.Checklist(
                id='columns-checklist',
                value=[],
                labelStyle={'display': 'block'}
            ),
            html.H3("X-axis"),
            html.Div(id='x-axis-fields'),
            html.H3("Y-axis"),
            html.Div(id='y-axis-fields')
        ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px', 'border': '1px solid black'}),

        html.Div([
            html.H3("Select Graph Type:"),
            dcc.RadioItems(
                id='graph-type',
                options=[
                    {'label': 'Bar', 'value': 'bar'},
                    {'label': 'Line', 'value': 'line'},
                    {'label': 'Pie', 'value': 'pie'},
                    {'label': 'Scatter', 'value': 'scatter'},
                    {'label': 'Area', 'value': 'area'},
                    {'label': 'Histogram', 'value': 'histogram'},
                    {'label': 'Box Plot', 'value': 'box'},
                    {'label': 'Violin Plot', 'value': 'violin'},
                    {'label': 'Funnel', 'value': 'funnel'},
                    {'label': 'Heatmap', 'value': 'heatmap'},
                    {'label': 'Stacked Bar', 'value': 'stack'}
                ],
                value='bar',
                labelStyle={'display': 'block'}
            ),
            html.H3("Legend"),
            html.Div(id='legend-fields'),
            dcc.Checklist(
                id='toggle-legend',
                options=[{'label': 'Show Legend', 'value': 'show'}],
                value=['show'],
                labelStyle={'display': 'block'}
            ),
            dcc.Checklist(
                id='drilldown-checkbox',
                options=[{'label': 'Enable Drill Down', 'value': 'enabled'}],
                value=[],
                labelStyle={'display': 'block'}
            ),
            html.Button('Back to Summary', id='reset-button', n_clicks=0)
        ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px', 'border': '1px solid black'}),

        # Graph display
        html.Div([
            dcc.Graph(id='graph')
        ], style={'width': '55%', 'display': 'inline-block', 'padding': '10px', 'border': '1px solid black'})
    ], style={'display': 'flex'})
])

# Global variables to store data and drilldown state
global_df = pd.DataFrame()
drilldown_level = 0
drilldown_history = []

# Callback to handle file upload and update columns
@app.callback(
    [Output('output-file-upload', 'children'),
     Output('columns-checklist', 'options')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(list_of_contents, list_of_names):
    global global_df
    if list_of_contents is not None:
        dfs = []
        filenames = []
        for contents, name in zip(list_of_contents, list_of_names):
            parsed_result = parse_contents(contents, name)
            if isinstance(parsed_result, tuple):
                df, filename = parsed_result
                dfs.append(df)
                filenames.append(filename)
            else:
                return parsed_result, []

        # Combine dataframes if multiple files are uploaded
        if len(dfs) > 1:
            combined_df = pd.concat(dfs, ignore_index=True)
        else:
            combined_df = dfs[0]

        # Update the global dataframe
        global_df = combined_df

        options = [{'label': col, 'value': col} for col in combined_df.columns]
        return html.Div([html.H5(filenames)]), options

    return html.Div("No files uploaded"), []

# Callback to update the fields for X-axis, Y-axis, and legend selection
@app.callback(
    [Output('x-axis-fields', 'children'),
     Output('y-axis-fields', 'children'),
     Output('legend-fields', 'children')],
    [Input('columns-checklist', 'value')]
)
def update_fields(selected_columns):
    if not selected_columns:
        return html.Div("No fields selected"), html.Div("No fields selected"), html.Div("No fields selected")
    
    x_axis_options = dcc.RadioItems(id='x-axis-column', options=[{'label': col, 'value': col} for col in selected_columns], labelStyle={'display': 'block'})
    y_axis_options = dcc.Checklist(id='y-axis-column', options=[{'label': col, 'value': col} for col in selected_columns], labelStyle={'display': 'block'})
    legend_options = dcc.RadioItems(id='legend-column', options=[{'label': col, 'value': col} for col in selected_columns], labelStyle={'display': 'block'})

    return x_axis_options, y_axis_options, legend_options

# Callback to update the graph and handle drill-down
@app.callback(
    Output('graph', 'figure'),
    [Input('x-axis-column', 'value'),
     Input('y-axis-column', 'value'),
     Input('graph-type', 'value'),
     Input('legend-column', 'value'),
     Input('reset-button', 'n_clicks'),
     Input('graph', 'clickData'),
     Input('toggle-legend', 'value'),
     Input('drilldown-checkbox', 'value')],
    [State('columns-checklist', 'value')]
)
def update_graph(x_col, y_cols, graph_type, legend_col, reset_n_clicks, click_data, toggle_legend, drilldown_value, selected_columns):
    global drilldown_level, global_df, drilldown_history
    ctx = callback_context

    if global_df.empty or not x_col or not y_cols:
        return {}

    show_legend = 'show' in toggle_legend
    drilldown_enabled = 'enabled' in drilldown_value

    # Reset drill-down
    if ctx.triggered and 'reset-button' in ctx.triggered[0]['prop_id']:
        drilldown_level = 0
        drilldown_history = []
        return generate_graph(global_df, x_col, y_cols, graph_type, legend_col, show_legend)

    # Handle drill-down
    if drilldown_enabled and click_data is not None:
        clicked_data = click_data['points'][0]['x']
        drilldown_history.append(clicked_data)
        if drilldown_level == 0 and 'Subcategory' in global_df.columns:
            drilldown_df = global_df[global_df[x_col] == clicked_data]
            drilldown_level += 1
            return generate_graph(drilldown_df, 'Subcategory', y_cols, graph_type, legend_col, show_legend)
        elif drilldown_level == 1 and 'Product' in global_df.columns:
            drilldown_df = global_df[global_df['Subcategory'] == clicked_data]
            drilldown_level += 1
            return generate_graph(drilldown_df, 'Product', y_cols, graph_type, legend_col, show_legend)
    
    return generate_graph(global_df, x_col, y_cols, graph_type, legend_col, show_legend)

def generate_graph(dataframe, x_col, y_cols, graph_type, legend_col, show_legend):
    if graph_type == 'bar':
        fig = px.bar(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'pie':
        if len(y_cols) == 1:
            fig = px.pie(dataframe, names=x_col, values=y_cols[0])
        else:
            return {}  # Pie charts can only display one value column
    elif graph_type == 'line':
        fig = px.line(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'scatter':
        fig = px.scatter(dataframe, x=x_col, y=y_cols[0], color=legend_col)
    elif graph_type == 'area':
        fig = px.area(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'histogram':
        fig = px.histogram(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'box':
        fig = px.box(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'violin':
        fig = px.violin(dataframe, x=x_col, y=y_cols, color=legend_col, box=True, points="all")
    elif graph_type == 'funnel':
        fig = px.funnel(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'heatmap':
        if len(y_cols) == 1:
            fig = px.density_heatmap(dataframe, x=x_col, y=y_cols[0], z=legend_col)
        else:
            return {}  # Heatmaps can only display one value column for z-axis
    elif graph_type == 'stack':
        fig = go.Figure(data=[
            go.Bar(name=col, x=dataframe[x_col], y=dataframe[col])
            for col in y_cols
        ])
        fig.update_layout(barmode='stack')
    else:
        fig = {}

    if not show_legend:
        fig.update_layout(showlegend=False)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

















































































