from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import io
import base64
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Dash app
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    files = request.files.getlist('file')
    for file in files:
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
    return redirect('/dash/')

# Dash app layout
dash_app.layout = html.Div([
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
        multiple=True  # Allow multiple files to be uploaded
    ),
    html.Div(id='output-data-upload'),
    dcc.Dropdown(id='x-axis-selector', placeholder="Select X-axis"),
    dcc.Dropdown(id='y-axis-selector', placeholder="Select Y-axis"),
    dcc.Dropdown(
        id='chart-type-selector',
        options=[
            {'label': 'Bar Chart', 'value': 'bar'},
            {'label': 'Line Chart', 'value': 'line'},
            {'label': 'Pie Chart', 'value': 'pie'},
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Stacked Bar', 'value': 'stack'}
        ],
        value='bar',
        placeholder="Select Chart Type"
    ),
    dcc.Graph(id='graph'),
    html.Hr(),
    html.H3('Drill Down View'),
    dcc.Dropdown(
        id='drilldown-chart-type-selector',
        options=[
            {'label': 'Bar Chart', 'value': 'bar'},
            {'label': 'Line Chart', 'value': 'line'},
            {'label': 'Pie Chart', 'value': 'pie'},
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Stacked Bar', 'value': 'stack'}
        ],
        value='bar',
        placeholder="Select Drilldown Chart Type"
    ),
    dcc.Graph(id='drilldown-graph')
])

# Callback to display uploaded files and parse content
@dash_app.callback(
    [Output('output-data-upload', 'children'),
     Output('x-axis-selector', 'options'),
     Output('y-axis-selector', 'options')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filenames):
    if contents is None:
        return html.Div(['No files uploaded yet.']), [], []
    
    data = []
    for content, filename in zip(contents, filenames):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        if filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(decoded))
        elif filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(decoded))
        df['Category'] = filename.split('.')[0]
        data.append(df)
    
    combined_df = pd.concat(data, ignore_index=True)
    options = [{'label': col, 'value': col} for col in combined_df.columns]

    return html.Div([
        html.H5('Files uploaded successfully.'),
        html.Hr(),
        html.Div(f"Uploaded files: {', '.join(filenames)}"),
        html.Hr()
    ]), options, options

# Callback to update the graph based on selected columns and chart type
@dash_app.callback(
    Output('graph', 'figure'),
    [Input('chart-type-selector', 'value'),
     Input('x-axis-selector', 'value'),
     Input('y-axis-selector', 'value')],
    [State('upload-data', 'contents'),
     State('upload-data', 'filename')]
)
def update_graph(chart_type, x_axis, y_axis, contents, filenames):
    if contents is None or x_axis is None or y_axis is None:
        raise PreventUpdate
    
    data = []
    for content, filename in zip(contents, filenames):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        if filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(decoded))
        elif filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(decoded))
        df['Category'] = filename.split('.')[0]
        data.append(df)
    
    combined_df = pd.concat(data, ignore_index=True)

    if combined_df.empty:
        return px.bar()

    if chart_type == 'bar':
        fig = px.bar(combined_df, x=x_axis, y=y_axis, color='Category', barmode='group')
    elif chart_type == 'line':
        fig = px.line(combined_df, x=x_axis, y=y_axis, color='Category')
    elif chart_type == 'pie':
        fig = px.pie(combined_df, names=x_axis, values=y_axis, title='Sales Distribution')
    elif chart_type == 'scatter':
        fig = px.scatter(combined_df, x=x_axis, y=y_axis, color='Category')
    elif chart_type == 'stack':
        fig = go.Figure(data=[
            go.Bar(name=col, x=combined_df[x_axis], y=combined_df[col])
            for col in combined_df[y_axis].unique()
        ])
        fig.update_layout(barmode='stack', title='Stacked Bar Chart')

    return fig

# Callback for drill-down to individual items on bar click
@dash_app.callback(
    Output('drilldown-graph', 'figure'),
    [Input('graph', 'clickData'),
     Input('drilldown-chart-type-selector', 'value')],
    [State('x-axis-selector', 'value'),
     State('y-axis-selector', 'value'),
     State('upload-data', 'contents'),
     State('upload-data', 'filename')],
    prevent_initial_call=True
)
def drill_down(clickData, drilldown_chart_type, x_axis, y_axis, contents, filenames):
    if clickData is None or x_axis is None or y_axis is None:
        raise PreventUpdate
    
    data = []
    for content, filename in zip(contents, filenames):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        if filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(decoded))
        elif filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(decoded))
        df['Category'] = filename.split('.')[0]
        data.append(df)
    
    combined_df = pd.concat(data, ignore_index=True)
    
    clicked_category = clickData['points'][0]['x']
    filtered_df = combined_df[combined_df['Category'] == clicked_category]

    if drilldown_chart_type == 'bar':
        fig = px.bar(filtered_df, x=x_axis, y=y_axis, color='Category', barmode='group', title=f'Detailed View for {clicked_category}')
    elif drilldown_chart_type == 'line':
        fig = px.line(filtered_df, x=x_axis, y=y_axis, color='Category', title=f'Detailed View for {clicked_category}')
    elif drilldown_chart_type == 'pie':
        fig = px.pie(filtered_df, names=x_axis, values=y_axis, title=f'Detailed View for {clicked_category}')
    elif drilldown_chart_type == 'scatter':
        fig = px.scatter(filtered_df, x=x_axis, y=y_axis, color='Category', title=f'Detailed View for {clicked_category}')
    elif drilldown_chart_type == 'stack':
        fig = go.Figure(data=[
            go.Bar(name=quarter, x=filtered_df[x_axis], y=filtered_df[filtered_df['Quarter'] == quarter][y_axis])
            for quarter in filtered_df['Quarter'].unique()
        ])
        fig.update_layout(barmode='stack', title=f'Stacked Bar Chart for {clicked_category}')

    return fig

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)


























# from flask import Flask, render_template, request, redirect, url_for
# import pandas as pd
# import os
# import io
# import base64
# from dash import Dash, dcc, html
# from dash.dependencies import Input, Output, State
# import plotly.express as px
# import plotly.graph_objects as go
# from dash.exceptions import PreventUpdate

# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Initialize Dash app
# dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')

# # Helper function to check allowed file extensions
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return redirect(request.url)
#     files = request.files.getlist('file')
#     for file in files:
#         if file.filename == '':
#             continue
#         if file and allowed_file(file.filename):
#             filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#             file.save(filename)
#     return redirect('/dash/')

# # Dash app layout
# dash_app.layout = html.Div([
#     dcc.Upload(
#         id='upload-data',
#         children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
#         style={
#             'width': '100%',
#             'height': '60px',
#             'lineHeight': '60px',
#             'borderWidth': '1px',
#             'borderStyle': 'dashed',
#             'borderRadius': '5px',
#             'textAlign': 'center',
#             'margin': '10px'
#         },
#         multiple=True  # Allow multiple files to be uploaded
#     ),
#     html.Div(id='output-data-upload'),
#     dcc.Dropdown(id='x-axis-selector', placeholder="Select X-axis"),
#     dcc.Dropdown(id='y-axis-selector', placeholder="Select Y-axis"),
#     dcc.Dropdown(
#         id='chart-type-selector',
#         options=[
#             {'label': 'Bar Chart', 'value': 'bar'},
#             {'label': 'Line Chart', 'value': 'line'},
#             {'label': 'Pie Chart', 'value': 'pie'},
#             {'label': 'Scatter Plot', 'value': 'scatter'},
#             {'label': 'Stacked Bar', 'value': 'stack'}
#         ],
#         value='bar',
#         placeholder="Select Chart Type"
#     ),
#     dcc.Graph(id='graph'),
#     html.Hr(),
#     html.H3('Drill Down View'),
#     dcc.Dropdown(
#         id='drilldown-chart-type-selector',
#         options=[
#             {'label': 'Bar Chart', 'value': 'bar'},
#             {'label': 'Line Chart', 'value': 'line'},
#             {'label': 'Pie Chart', 'value': 'pie'},
#             {'label': 'Scatter Plot', 'value': 'scatter'},
#             {'label': 'Stacked Bar', 'value': 'stack'}
#         ],
#         value='bar',
#         placeholder="Select Drilldown Chart Type"
#     ),
#     dcc.Graph(id='drilldown-graph')
# ])

# # Callback to display uploaded files and parse content
# @dash_app.callback(
#     [Output('output-data-upload', 'children'),
#      Output('x-axis-selector', 'options'),
#      Output('y-axis-selector', 'options')],
#     [Input('upload-data', 'contents')],
#     [State('upload-data', 'filename')]
# )
# def update_output(contents, filenames):
#     if contents is None:
#         return html.Div(['No files uploaded yet.']), [], []
    
#     data = []
#     for content, filename in zip(contents, filenames):
#         content_type, content_string = content.split(',')
#         decoded = base64.b64decode(content_string)
#         if filename.endswith('.xlsx'):
#             df = pd.read_excel(io.BytesIO(decoded))
#         elif filename.endswith('.csv'):
#             df = pd.read_csv(io.BytesIO(decoded))
#         df['Category'] = filename.split('.')[0]
#         data.append(df)
    
#     combined_df = pd.concat(data, ignore_index=True)
#     options = [{'label': col, 'value': col} for col in combined_df.columns]

#     return html.Div([
#         html.H5('Files uploaded successfully.'),
#         html.Hr(),
#         html.Div(f"Uploaded files: {', '.join(filenames)}"),
#         html.Hr()
#     ]), options, options

# # Callback to update the graph based on selected columns and chart type
# @dash_app.callback(
#     Output('graph', 'figure'),
#     [Input('chart-type-selector', 'value'),
#      Input('x-axis-selector', 'value'),
#      Input('y-axis-selector', 'value')],
#     [State('upload-data', 'contents'),
#      State('upload-data', 'filename')]
# )
# def update_graph(chart_type, x_axis, y_axis, contents, filenames):
#     if contents is None or x_axis is None or y_axis is None:
#         raise PreventUpdate
    
#     data = []
#     for content, filename in zip(contents, filenames):
#         content_type, content_string = content.split(',')
#         decoded = base64.b64decode(content_string)
#         if filename.endswith('.xlsx'):
#             df = pd.read_excel(io.BytesIO(decoded))
#         elif filename.endswith('.csv'):
#             df = pd.read_csv(io.BytesIO(decoded))
#         df['Category'] = filename.split('.')[0]
#         data.append(df)
    
#     combined_df = pd.concat(data, ignore_index=True)

#     if combined_df.empty:
#         return px.bar()

#     if chart_type == 'bar':
#         fig = px.bar(combined_df, x=x_axis, y=y_axis, color='Category', barmode='group')
#     elif chart_type == 'line':
#         fig = px.line(combined_df, x=x_axis, y=y_axis, color='Category')
#     elif chart_type == 'pie':
#         fig = px.pie(combined_df, names=x_axis, values=y_axis, title='Sales Distribution')
#     elif chart_type == 'scatter':
#         fig = px.scatter(combined_df, x=x_axis, y=y_axis, color='Category')
#     elif chart_type == 'stack':
#         fig = go.Figure(data=[
#             go.Bar(name=col, x=combined_df[x_axis], y=combined_df[col])
#             for col in combined_df[y_axis].unique()
#         ])
#         fig.update_layout(barmode='stack', title='Stacked Bar Chart')

#     return fig

# # Callback for drill-down to individual items on bar click
# @dash_app.callback(
#     Output('drilldown-graph', 'figure'),
#     [Input('graph', 'clickData'),
#      Input('drilldown-chart-type-selector', 'value')],
#     [State('x-axis-selector', 'value'),
#      State('y-axis-selector', 'value'),
#      State('upload-data', 'contents'),
#      State('upload-data', 'filename')],
#     prevent_initial_call=True
# )
# def drill_down(clickData, drilldown_chart_type, x_axis, y_axis, contents, filenames):
#     if clickData is None or x_axis is None or y_axis is None:
#         raise PreventUpdate
    
#     data = []
#     for content, filename in zip(contents, filenames):
#         content_type, content_string = content.split(',')
#         decoded = base64.b64decode(content_string)
#         if filename.endswith('.xlsx'):
#             df = pd.read_excel(io.BytesIO(decoded))
#         elif filename.endswith('.csv'):
#             df = pd.read_csv(io.BytesIO(decoded))
#         df['Category'] = filename.split('.')[0]
#         data.append(df)
    
#     combined_df = pd.concat(data, ignore_index=True)
    
#     clicked_category = clickData['points'][0]['x']
#     filtered_df = combined_df[combined_df['Category'] == clicked_category]

#     if drilldown_chart_type == 'bar':
#         fig = px.bar(filtered_df, x=x_axis, y=y_axis, color='Category', barmode='group', title=f'Detailed View for {clicked_category}')
#     elif drilldown_chart_type == 'line':
#         fig = px.line(filtered_df, x=x_axis, y=y_axis, color='Category', title=f'Detailed View for {clicked_category}')
#     elif drilldown_chart_type == 'pie':
#         fig = px.pie(filtered_df, names=x_axis, values=y_axis, title=f'Detailed View for {clicked_category}')
#     elif drilldown_chart_type == 'scatter':
#         fig = px.scatter(filtered_df, x=x_axis, y=y_axis, color='Category', title=f'Detailed View for {clicked_category}')
#     elif drilldown_chart_type == 'stack':
#         fig = go.Figure(data=[
#             go.Bar(name=quarter, x=filtered_df[x_axis], y=filtered_df[filtered_df['Quarter'] == quarter][y_axis])
#             for quarter in filtered_df['Quarter'].unique()
#         ])
#         fig.update_layout(barmode='stack', title=f'Stacked Bar Chart for {clicked_category}')

#     return fig

# if __name__ == '__main__':
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)
#     app.run(debug=True)
























































































