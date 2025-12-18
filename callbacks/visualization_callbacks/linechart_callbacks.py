from dash import dcc, Input, Output, State, no_update
import plotly.express as px
from dash.dependencies import MATCH
import pandas as pd

def register_linechart_callbacks(app):

    @app.callback(Output({'index':MATCH, 'type':'value_filter-line'}, 'options'),
              Input({'index':MATCH, 'type':'filter-line'}, 'value'),
              State('storage','data'),
              prevent_initial_call=False)
    def set_options_line(filter_col, storage):
        data = storage['data']['df']
        df = pd.read_json(data, orient='records')
        
        if not filter_col:
            return no_update
        return df[filter_col].unique()

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
               Input({'index':MATCH, 'type':'xaxis'},'value'),
               Input({'index':MATCH, 'type':'yaxis'}, 'value'),
               Input({'index':MATCH, 'type':'agg-line'}, 'value'),
               Input({'index':MATCH, 'type':'filter-line'}, 'value'),
               Input({'index':MATCH, 'type':'value_filter-line'}, 'value'),
               Input({'index':MATCH, 'type':'name-chart'},'value'),
               Input({'index':MATCH, 'type':'sheet'}, 'value'),
               Input('template', 'value'),
               State('storage','data'),
              prevent_initial_call=True)
    def make_line(x_data, y_data, agg_data, filter_col, value_filter, linechart_name, sheet, template, storage):

        data = storage['data']['df']
        hidden_columns = storage['data']['hidden_columns']
        
        if not x_data or not y_data:
            return []
        ### dictionary for an aggregation ###
        d = {'sum': 'sum()', 'avg':'mean()', 'count': 'count()', 'countd': 'nunique()', 'min':'min()', 'max':'max()'}

        df = pd.read_json(data, orient='records')
        cols = ['NA'] if 'NA' in df.columns else []
        cols += hidden_columns if hidden_columns else []
        df = df.drop(columns = cols)

        if filter_col and value_filter:
            df = df.loc[df[filter_col].isin(value_filter)]

        nnn = df.groupby(x_data)[y_data]
        r = {'nnn':nnn}
        exec('nnn = nnn.'+d[agg_data], r)

        line_fig = px.line(r['nnn'], x=r['nnn'].index, y=y_data, color_discrete_sequence=px.colors.qualitative.Plotly, template = template)
        line_fig.update_layout(
            title={
                'text': linechart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        return dcc.Graph(figure=line_fig)