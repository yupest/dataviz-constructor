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

def register_piechart_callbacks(app):
    @app.callback(Output({'index':MATCH, 'type':'sheet'},'label', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'style', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'selected_style', allow_duplicate=True),
              Input({'index':MATCH, 'type':'name-pie'},'value'),
              prevent_initial_call=True)
    def rename_sheet_pie(name):
        # print(name)
        style = {**tab_style, **custom_style_tab, 'background-image':"url('https://github.com/yupest/nto/blob/master/src/pie.png?raw=true')"}
        if not name:
            return no_update, style, style
        else:

            return name, style, style

    @app.callback(Output({'index':MATCH, 'type':'value_filter-pie'}, 'options'),
              Input({'index':MATCH, 'type':'filter-pie'}, 'value'),
              State('storage','data'),
              prevent_initial_call=False)
    def set_options_pie(filter_col, storage):
        data = storage['data']['df']
        df = pd.read_json(data, orient='records')
        if not filter_col:
            return no_update
        return df[filter_col].unique()

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
               Input({'index':MATCH, 'type':'xaxis'},'value'),
               Input({'index':MATCH, 'type':'yaxis'}, 'value'),
               Input({'index':MATCH, 'type':'sectors-slider'}, 'value'),
               Input({'index':MATCH, 'type':'agg-pie'}, 'value'),
               Input({'index':MATCH, 'type':'filter-pie'}, 'value'),
               Input({'index':MATCH, 'type':'value_filter-pie'}, 'value'),
               Input({'index':MATCH, 'type':'name-pie'},'value'),
               Input({'index':MATCH, 'type':'sheet'}, 'value'),
               State('storage','data'),
              prevent_initial_call=True)
    def make_pie(x_data, y_data, sliderSectors, agg_data, filter_col, value_filter, piechart_name, sheet, storage):
        data = storage['data']['df']
        hidden_columns = storage['data']['hidden_columns']
        
        df = pd.read_json(data, orient='records')
        
        d = {'sum': 'sum()', 'avg':'mean()', 'count': 'count()', 'countd': 'nunique()', 'min':'min()', 'max':'max()'}
        
        cols = ['NA'] if 'NA' in df.columns else []
        cols += hidden_columns if hidden_columns else []
        df = df.drop(columns = cols)

        if filter_col and value_filter:
            df = df.loc[df[filter_col].isin(value_filter)]

        df_temp = df[[x_data, y_data]].groupby(by=x_data)
        r = {'df_temp':df_temp}
        exec('df_temp = df_temp.'+d[agg_data], r)

        df_temp = r['df_temp']

        if df_temp.shape[0] > sliderSectors:
             df_temp = df_temp.sort_values(y_data, ascending = False).reset_index()
             df_temp.loc[sliderSectors:, x_data] = 'Другое'
             df_temp = df_temp.groupby(x_data).sum()

        pie_fig = px.pie(df_temp, values=y_data, names=df_temp.index, color_discrete_sequence=px.colors.qualitative.Plotly)
        pie_fig.update_layout(
            title={
                'text': piechart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        pie_fig.update_traces(
             textposition="inside",
             textinfo='percent+label'

        )

        return dcc.Graph(figure=pie_fig)
