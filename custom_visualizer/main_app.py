from dash import Dash, html, dcc, dash_table

from OptionChanger import OptionChanger
import helpers

options = OptionChanger()

app = Dash()

text_style = {'fostSize': 20, 'font-family': 'Georgia'}

# Requires Dash 2.17.0 or later
app.layout = [
    html.Div(children='MVSplat Visualizer', style={'textAlign': 'center', 'fontSize': 30, 'font-weight': 'bold', 'font-family': 'Georgia'}),
    html.Div(children='By Elena-Oana Milchi', style={'textAlign': 'center', 'fontSize': 20, 'font-weight': 'bold', 'font-family': 'Georgia'}),
    html.Hr(),
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Montréal'},
                    ],
                    'layout': {
                        'title': 'Dash Data Visualization'
                    }
                }
            )
        ], style={'width': '75%'}),
        html.Div(children=[
            dcc.Checklist(
                ['Cost Volume Refinement', 'Depth Refinement', 'Use cross attention', 'Use epipolar transformer'],
                ['Cost Volume Refinement', 'Depth Refinement', 'Use cross attention', 'Use epipolar transformer'],
                labelStyle=text_style
            )
        ], style={'width': '25%'})
    ], style={'display': 'flex', 'gap': '10px'})
]

if __name__ == '__main__':

    helpers.init_configs()

    app.run(debug=True)