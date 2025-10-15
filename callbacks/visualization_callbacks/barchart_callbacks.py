from dash import dcc, Input, Output, State, no_update
import plotly.express as px
from dash.dependencies import MATCH
import pandas as pd
import json

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

def register_barchart_callbacks(app):

    @app.callback(Output({'index':MATCH, 'type':'top-slider-bar'}, 'disabled'),
              Input({'index':MATCH, 'type':'creation-top-bar'}, 'value'),
              prevent_initial_call=True)
    def update_disabled_top_slider(value):
        return value == []

    @app.callback(Output({'index':MATCH, 'type':'sheet'},'label', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'style', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'selected_style', allow_duplicate=True),
              Input({'index':MATCH, 'type':'name-bar'},'value'),
              State({'index':MATCH, 'type':'sheet'},'value'),
              prevent_initial_call=True)
    def rename_sheet_bar(name, value):
        print(name)
        style = {**tab_style, **custom_style_tab, 'background-image':"url('https://github.com/yupest/nto/blob/master/src/bar.png?raw=true')"}
        if not name:
            return value, style, style
        else:

            return name, style, style

    @app.callback(Output({'index':MATCH, 'type':'value_filter-bar'}, 'options'),
              Input('df-table','data'),
              Input({'index':MATCH, 'type':'filter-bar'}, 'value'),
              prevent_initial_call=False)
    def set_options_bar(data, filter_col):
        df = pd.read_json(json.dumps(data), orient='records')
        if not filter_col:
            return no_update
        return df[filter_col].unique()

    @app.callback([Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
                   Output({'index':MATCH, 'type':'dashboard'}, 'children', allow_duplicate=True)],
                  [Input('data-file','data'),
                   Input('df-table','hidden_columns'),
                   Input({'index':MATCH, 'type':'xaxis'},'value'),
                   Input({'index':MATCH, 'type':'yaxis'}, 'value'),
                   Input({'index':MATCH, 'type':'agg-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'name-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'creation-top-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'top-slider-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'filter-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'value_filter-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'orientation'}, 'value')],
                   prevent_initial_call=True)
    def make_bar(data, hidden_columns, x_data, y_data, agg_data, barchart_name, creation_top, top_slider, filter_col, value_filter, orientation):

        if not x_data or not y_data:
            print('no', x_data, y_data)
            return no_update, no_update

        ### dictionary for an aggregation ###
        d = {'sum': 'sum()', 'avg':'mean()', 'count': 'count()', 'countd': 'nunique()', 'min':'min()', 'max':'max()'}

        df = pd.read_json(data['data'], orient='records')
        cols = ['NA'] if 'NA' in df.columns else []
        cols += hidden_columns if hidden_columns else []
        df = df.drop(columns = cols)

        if filter_col and value_filter:
            df = df.loc[df[filter_col].isin(value_filter)]

        nnn = df.groupby(x_data)[y_data]
        r = {'nnn':nnn}
        exec('nnn = nnn.'+d[agg_data], r)

        y_axis = agg_data+'('+y_data[0]+')' if len(y_data)==1 else 'value'

        o = None
        if orientation:
            o = 'h'
            df_temp = r['nnn'].sort_values(y_data, ascending = True)
            for y_col in y_data:
                df_temp = df_temp.loc[~df_temp[y_col].isna()]

            if creation_top:
                df_temp = df_temp.tail(top_slider)

            x = y_data[0] if len(y_data)==1 else y_data
            y = df_temp.index
        else:
            df_temp = r['nnn'].sort_values(y_data, ascending = False)

            if creation_top:
                df_temp = df_temp[:top_slider]

            x = df_temp.index
            y = y_data[0] if len(y_data)==1 else y_data

        bar_fig = px.bar(df_temp, x=x, y=y, labels={'y':y_axis,'x': x_data}, orientation = o)
        bar_fig.update_layout(
            title={
                'text': barchart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
            }
        )
        return dcc.Graph(figure=bar_fig), dcc.Graph(figure=bar_fig, responsive=True, style={"min-height":"0","flex-grow":"1"})