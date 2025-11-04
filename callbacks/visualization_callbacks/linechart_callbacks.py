from dash import dcc, Input, Output, no_update
import plotly.express as px
from dash.dependencies import MATCH
import pandas as pd
import json
import io

# TODO: убрать стилевые константы в отдельный файл
tab_style = {
    'padding': '10px 10px',  # Универсальные отступы
    'display': 'flex',
    'alignItems': 'center',  # Вертикальное выравнивание содержимого
    'justifyContent': 'center',  # Горизонтальное выравнивание
    'textAlign': 'center',
}
custom_style_tab = {
    'background-repeat': 'no-repeat',
    'background-position': '10px center',
    'background-size': '25px',
    'padding-left': '35px' }

def register_linechart_callbacks(app):
    @app.callback(Output({'index':MATCH, 'type':'sheet'},'label', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'style', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'selected_style', allow_duplicate=True),
              Input({'index':MATCH, 'type':'name-line'},'value'),
              prevent_initial_call=True)
    def rename_sheet_line(name):
        print(name)
        style = {**tab_style, **custom_style_tab, 'background-image':"url('https://github.com/yupest/nto/blob/master/src/line.png?raw=true')"}
        if not name:
            return no_update, style, style
        else:
            return name, style, style

    @app.callback(Output({'index':MATCH, 'type':'value_filter-line'}, 'options'),
              Input('df-table','data'),
              Input({'index':MATCH, 'type':'filter-line'}, 'value'),
              prevent_initial_call=False)
    def set_options_line(data, filter_col):
        df = pd.read_json(io.StringIO(json.dumps(data)), orient='records')
        if not filter_col:
            return no_update
        return df[filter_col].unique()

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
               Input('df-table','data'),
               Input('df-table','hidden_columns'),
               Input({'index':MATCH, 'type':'xaxis'},'value'),
               Input({'index':MATCH, 'type':'yaxis'}, 'value'),
               Input({'index':MATCH, 'type':'agg-line'}, 'value'),
               Input({'index':MATCH, 'type':'filter-line'}, 'value'),
               Input({'index':MATCH, 'type':'value_filter-line'}, 'value'),
               Input({'index':MATCH, 'type':'name-line'},'value'),
              prevent_initial_call=True)
    def make_line(data, hidden_columns, x_data, y_data, agg_data, filter_col, value_filter, linechart_name):

        if not x_data or not y_data:
            return []
        ### dictionary for an aggregation ###
        d = {'sum': 'sum()', 'avg':'mean()', 'count': 'count()', 'countd': 'nunique()', 'min':'min()', 'max':'max()'}

        df = pd.read_json(json.dumps(data), orient='records')
        cols = ['NA'] if 'NA' in df.columns else []
        cols += hidden_columns if hidden_columns else []
        df = df.drop(columns = cols)

        if filter_col and value_filter:
            df = df.loc[df[filter_col].isin(value_filter)]

        nnn = df.groupby(x_data)[y_data]
        r = {'nnn':nnn}
        exec('nnn = nnn.'+d[agg_data], r)

        line_fig = px.line(r['nnn'], x=r['nnn'].index, y=y_data, color_discrete_sequence=px.colors.qualitative.Plotly)
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
