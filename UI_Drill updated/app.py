import pandas as pd
import base64
import io
from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.express as px
import plotly.graph_objects as go
from flask_caching import Cache

# Initialize the Dash app
app = Dash(__name__)
app.config.suppress_callback_exceptions = True
cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})

TIMEOUT = 600  # Cache timeout in seconds

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
    html.H1("Data Visualization Tool", style={'text-align': 'center', 'margin-bottom': '20px'}),

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
            'margin-bottom': '20px'
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
                    {'label': 'Column', 'value': 'column'},
                    {'label': 'Line', 'value': 'line'},
                    {'label': 'Pie', 'value': 'pie'},
                    {'label': 'Donut', 'value': 'donut'},
                    {'label': 'Area', 'value': 'area'},
                    {'label': 'Scatter', 'value': 'scatter'},
                    {'label': 'Bubble', 'value': 'bubble'},
                    {'label': 'Stacked Bar', 'value': 'stacked_bar'},
                    {'label': '100% Stacked Bar', 'value': 'stacked_bar_100'},
                    {'label': 'Stacked Column', 'value': 'stacked_column'},
                    {'label': '100% Stacked Column', 'value': 'stacked_column_100'},
                    {'label': 'Map', 'value': 'map'},
                    {'label': 'Filled Map', 'value': 'filled_map'},
                    {'label': 'TreeMap', 'value': 'treemap'},
                    {'label': 'Waterfall', 'value': 'waterfall'},
                    {'label': 'Funnel', 'value': 'funnel'},
                    {'label': 'Gauge', 'value': 'gauge'},
                    {'label': 'KPI', 'value': 'kpi'},
                    {'label': 'Table', 'value': 'table'},
                    {'label': 'Matrix', 'value': 'matrix'},
                    {'label': 'Card', 'value': 'card'},
                    {'label': 'Multi-Row Card', 'value': 'multi_row_card'},
                    {'label': 'Slicer', 'value': 'slicer'}
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
            )
        ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px', 'border': '1px solid black'}),

        # Graph display
        html.Div([
            dcc.Graph(id='graph'),
            html.Div([
                html.Button('Drill Down', id='drilldown-button', n_clicks=0),
                html.Button('Drill Up', id='drillup-button', n_clicks=0, style={'margin-left': '10px'}),
                html.Button('Reset', id='reset-button', n_clicks=0, style={'margin-left': '10px'})
            ], style={'margin-top': '10px', 'text-align': 'center'})
        ], style={'width': '55%', 'display': 'inline-block', 'padding': '10px', 'border': '1px solid black'})
    ], style={'display': 'flex'}),

    # X-axis Drill-down options
    html.Div([
        html.H3("X-axis Drill Down"),
        dcc.Dropdown(id='x-axis-drilldown', multi=True)
    ], style={'padding': '10px', 'border': '1px solid black', 'margin-top': '20px'})
])

# Global variables to store data and drilldown state
global_df = pd.DataFrame()
drilldown_level = 0
drilldown_history = []

@cache.memoize(timeout=TIMEOUT)
def get_dataframe(contents, filename):
    return parse_contents(contents, filename)

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
            parsed_result = get_dataframe(contents, name)
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

# Callback to update the fields for X-axis, Y-axis, legend, and X-axis drilldown selection
@app.callback(
    [Output('x-axis-fields', 'children'),
     Output('y-axis-fields', 'children'),
     Output('legend-fields', 'children'),
     Output('x-axis-drilldown', 'options')],
    [Input('columns-checklist', 'value')]
)
def update_fields(selected_columns):
    if not selected_columns:
        return (html.Div("No fields selected"), html.Div("No fields selected"), html.Div("No fields selected"), [])
    
    x_axis_options = dcc.RadioItems(id='x-axis-column', options=[{'label': col, 'value': col} for col in selected_columns], labelStyle={'display': 'block'})
    y_axis_options = dcc.Checklist(id='y-axis-column', options=[{'label': col, 'value': col} for col in selected_columns], labelStyle={'display': 'block'})
    legend_options = dcc.RadioItems(id='legend-column', options=[{'label': col, 'value': col} for col in selected_columns], labelStyle={'display': 'block'})
    dropdown_options = [{'label': col, 'value': col} for col in selected_columns]

    return x_axis_options, y_axis_options, legend_options, dropdown_options

# Callback to update the graph and handle drill-down
@app.callback(
    Output('graph', 'figure'),
    [Input('x-axis-column', 'value'),
     Input('y-axis-column', 'value'),
     Input('graph-type', 'value'),
     Input('legend-column', 'value'),
     Input('reset-button', 'n_clicks'),
     Input('drilldown-button', 'n_clicks'),
     Input('drillup-button', 'n_clicks'),
     Input('toggle-legend', 'value'),
     Input('x-axis-drilldown', 'value')],
    [State('graph', 'clickData'),
     State('columns-checklist', 'value')]
)
def update_graph(x_col, y_cols, graph_type, legend_col, reset_n_clicks, drilldown_n_clicks, drillup_n_clicks, toggle_legend, x_drilldown, click_data, selected_columns):
    global drilldown_level, global_df, drilldown_history
    ctx = callback_context

    if global_df.empty or not x_col or not y_cols:
        return {}

    show_legend = 'show' in toggle_legend
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Reset drill-down
    if triggered_id == 'reset-button':
        drilldown_level = 0
        drilldown_history = []
        return generate_graph(global_df, x_col, y_cols, graph_type, legend_col, show_legend)

    # Handle drill-down
    if triggered_id == 'drilldown-button' and click_data is not None:
        clicked_data = click_data['points'][0]['x']
        drilldown_history.append((x_col, clicked_data))
        
        if drilldown_level < len(x_drilldown):
            next_x_col = x_drilldown[drilldown_level]
            drilldown_df = global_df[global_df[x_col] == clicked_data]
            drilldown_level += 1
            return generate_graph(drilldown_df, next_x_col, y_cols, graph_type, legend_col, show_legend)

    # Handle drill-up
    if triggered_id == 'drillup-button' and drilldown_level > 0:
        drilldown_level -= 1
        if drilldown_level == 0:
            drilldown_history = []
            return generate_graph(global_df, x_col, y_cols, graph_type, legend_col, show_legend)
        else:
            previous_x_col, clicked_data = drilldown_history[-1]
            drilldown_df = global_df[global_df[previous_x_col] == clicked_data]
            drilldown_history.pop()
            return generate_graph(drilldown_df, previous_x_col, y_cols, graph_type, legend_col, show_legend)
    
    return generate_graph(global_df, x_col, y_cols, graph_type, legend_col, show_legend)

def generate_graph(dataframe, x_col, y_cols, graph_type, legend_col, show_legend):
    if graph_type == 'bar':
        fig = px.bar(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'column':
        fig = px.bar(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'line':
        fig = px.line(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'pie':
        if len(y_cols) == 1:
            fig = px.pie(dataframe, names=x_col, values=y_cols[0])
        else:
            return {}  # Pie charts can only display one value column
    elif graph_type == 'donut':
        if len(y_cols) == 1:
            fig = px.pie(dataframe, names=x_col, values=y_cols[0], hole=0.3)
        else:
            return {}  # Donut charts can only display one value column
    elif graph_type == 'area':
        fig = px.area(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'scatter':
        fig = px.scatter(dataframe, x=x_col, y=y_cols[0], color=legend_col)
    elif graph_type == 'bubble':
        if len(y_cols) > 1:
            fig = px.scatter(dataframe, x=x_col, y=y_cols[0], size=y_cols[1], color=legend_col)
        else:
            return {}  # Bubble charts need at least two value columns
    elif graph_type in ['stacked_bar', 'stacked_column']:
        fig = px.bar(dataframe, x=x_col, y=y_cols, color=legend_col, barmode='stack')
    elif graph_type in ['stacked_bar_100', 'stacked_column_100']:
        fig = px.bar(dataframe, x=x_col, y=y_cols, color=legend_col, barmode='stack', text_auto='.2%')
    elif graph_type == 'map':
        fig = px.scatter_mapbox(dataframe, lat='Latitude', lon='Longitude', color=legend_col, size=y_cols[0])
        fig.update_layout(mapbox_style="open-street-map")
    elif graph_type == 'filled_map':
        fig = px.choropleth_mapbox(dataframe, geojson=None, locations='Store', color=y_cols[0], lat='Latitude', lon='Longitude')
        fig.update_layout(mapbox_style="open-street-map")
    elif graph_type == 'treemap':
        fig = px.treemap(dataframe, path=[x_col, legend_col], values=y_cols[0])
    elif graph_type == 'waterfall':
        fig = px.waterfall(dataframe, x=x_col, y=y_cols[0], color=legend_col)
    elif graph_type == 'funnel':
        fig = px.funnel(dataframe, x=x_col, y=y_cols, color=legend_col)
    elif graph_type == 'gauge':
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=dataframe[y_cols[0]].sum(),
            gauge={'axis': {'range': [None, 100]}}
        ))
    elif graph_type == 'kpi':
        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=dataframe[y_cols[0]].sum(),
            delta={'reference': dataframe[y_cols[0]].mean()}
        ))
    elif graph_type == 'table':
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(dataframe.columns)),
            cells=dict(values=[dataframe[col] for col in dataframe.columns])
        )])
    elif graph_type == 'matrix':
        fig = go.Figure(data=[go.Heatmap(
            z=dataframe[y_cols[0]],
            x=dataframe[x_col],
            y=dataframe[legend_col]
        )])
    elif graph_type == 'card':
        fig = go.Figure(go.Indicator(
            mode="number",
            value=dataframe[y_cols[0]].sum()
        ))
    elif graph_type == 'multi_row_card':
        fig = go.Figure(data=[go.Indicator(
            mode="number",
            value=dataframe[y_cols[0]].sum(),
            title={"text": legend_col}
        )])
    elif graph_type == 'slicer':
        # Slicers are not visualizations but filters; handling it separately might be needed
        return {}

    if not show_legend:
        fig.update_layout(showlegend=False)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
















































































