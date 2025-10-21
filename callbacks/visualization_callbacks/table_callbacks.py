from dash import dcc, Input, Output, no_update
import plotly.express as px
from dash.dependencies import MATCH
import numpy as np
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

def register_table_callbacks(app):
   
    @app.callback(Output({'index':MATCH, 'type':'menu-columns-table'}, 'style'),
              Output({'index':MATCH, 'type':'correlation-type-table'}, 'style'),
              Input({'index':MATCH, 'type':'correlation'}, 'value'),
              prevent_initial_call=False)
    def update_disabled_columns(value):
        not_value = {'display':'none'} if value==[] else {}
        value = {} if value==[] else {'display':'none'}
        # print(value, not_value)
        return value, not_value

    @app.callback(Output({'index':MATCH, 'type':'sheet'},'label', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'style', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'selected_style', allow_duplicate=True),
              Input({'index':MATCH, 'type':'name-table'},'value'),
              prevent_initial_call=True)
    def rename_sheet_table(name):
        print(name)
        style = {**tab_style, **custom_style_tab, 'background-image':"url('https://github.com/yupest/nto/blob/master/src/table.png?raw=true')"}
        if not name:
            return no_update, style, style
        else:

            return name, style, style

    @app.callback(Output({'index':MATCH, 'type':'value_filter-table'}, 'options'),
              Input('df-table','data'),
              Input({'index':MATCH, 'type':'filter-table'}, 'value'),
              prevent_initial_call=False)
    def set_options_table(data, filter_col):
        df = pd.read_json(json.dumps(data), orient='records')
        if not filter_col:
            return no_update
        return df[filter_col].unique()

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
                Input('df-table','data'),
                Input('df-table','hidden_columns'),
                Input({'index':MATCH, 'type':'correlation'}, 'value'),
                Input({'index':MATCH, 'type':'xaxis-table'},'value'),
                Input({'index':MATCH, 'type':'yaxis-table'}, 'value'),
                Input({'index':MATCH, 'type':'zaxis-table'}, 'value'),
                Input({'index':MATCH, 'type':'correlation-type-table'}, 'value'),
                Input({'index':MATCH, 'type':'agg-table'}, 'value'),
                Input({'index':MATCH, 'type':'filter-table'}, 'value'),
                Input({'index':MATCH, 'type':'value_filter-table'}, 'value'),
                Input({'index':MATCH, 'type':'name-table'},'value'),
                prevent_initial_call=True)
    def make_table(data, hidden_columns, correlation, x_data, y_data, z_data, corr_type, agg_data, filter_col, value_filter, chart_name):
        df = pd.read_json(json.dumps(data), orient='records')
        cols = ['NA'] if 'NA' in df.columns else []
        cols += hidden_columns if hidden_columns else []
        df = df.drop(columns = cols)
        if filter_col and value_filter:
            df = df.loc[df[filter_col].isin(value_filter)]

        if correlation:
            cols = df.columns[np.array([df[i].dtype != 'object' for i in df.columns])].tolist()
            table_chart = px.imshow(df[cols].corr(corr_type).round(3), text_auto=True, aspect="auto")

        else:
            ### dictionary for an aggregation ###
            d = {'sum': 'sum()', 'avg':'mean()', 'count': 'count()', 'countd': 'nunique()', 'min':'min()', 'max':'max()'}

            if not all([x_data, y_data, z_data]):
                return []

            nnn = df.groupby([x_data, y_data])[z_data]
            r = {'nnn':nnn}
            exec('nnn = nnn.'+d[agg_data], r)

            df_temp = r['nnn'].reset_index().pivot(index=x_data, columns=y_data, values=z_data)
            table_chart = px.imshow(df_temp.round(3), text_auto=True, zmax = df_temp.stack().quantile(0.75), zmin = df_temp.min().min(), aspect="auto")

        table_chart.update_layout(
            title={
                'text': chart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis = {'showgrid':False},
            yaxis = {'showgrid':False}
        )

        return dcc.Graph(figure=table_chart)