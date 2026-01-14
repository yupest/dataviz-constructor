from dash import dcc, Input, State, Output, no_update
import plotly.express as px
from dash.dependencies import MATCH
import pandas as pd
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

def register_barchart_callbacks(app):

    @app.callback(Output({'index':MATCH, 'type':'top-slider-bar'}, 'disabled'),
              Input({'index':MATCH, 'type':'creation-top-bar'}, 'value'),
              prevent_initial_call=True)
    def update_disabled_top_slider(value):
        return value == []

    @app.callback(Output({'index':MATCH, 'type':'value_filter-bar'}, 'options'),
              Input({'index':MATCH, 'type':'filter-bar'}, 'value'),
              State('storage','data'),
              prevent_initial_call=False)
    def set_options_bar(filter_col, storage):
        data = storage['data']['df']
        df = pd.read_json(io.StringIO(data), orient='records')
        if not filter_col:
            return no_update
        if filter_col == 'Названия метрик':
            return storage['data']['columns']['numeric']+storage['data']['columns']['discrete']
        
        return df[filter_col].unique()

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
                   Input({'index':MATCH, 'type':'xaxis'},'value'),
                   Input({'index':MATCH, 'type':'yaxis'}, 'value'),
                   Input({'index':MATCH, 'type':'agg-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'name-chart'}, 'value'),
                   Input({'index':MATCH, 'type':'creation-top-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'top-slider-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'filter-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'value_filter-bar'}, 'value'),
                   Input({'index':MATCH, 'type':'orientation'}, 'value'),
                   Input({'index':MATCH, 'type':'sheet'}, 'value'),
                   Input({'index':MATCH, 'type':'barmode'}, 'value'),
                   Input('template', 'value'),
                   State('storage','data'),
                   prevent_initial_call=True)
    def make_bar(x_data, y_data, agg_data, barchart_name, creation_top, top_slider, filter_col, value_filter, orientation, sheet, barmode, template, storage):

        if not x_data or not y_data:
            return []
        ### dictionary for an aggregation ###
        d = {'sum': 'sum()', 'avg':'mean()', 'count': 'count()', 'countd': 'nunique()', 'min':'min()', 'max':'max()'}

        data = storage['data']['df']
        hidden_columns = storage['data']['hidden_columns']
        df = pd.read_json(data, orient='records')
        
        cols = ['NA'] if 'NA' in df.columns else []
        cols += hidden_columns if hidden_columns else []
        df = df.drop(columns = cols)

        measure_names = storage['data']['columns']['numeric']+storage['data']['columns']['discrete']
        if filter_col and value_filter:
            if filter_col == 'Названия метрик':
                measure_names = value_filter
            else:
                df = df.loc[df[filter_col].isin(value_filter)]

        if x_data == 'Названия метрик' and y_data[0] == 'Значения метрик':
            y_data = f'{agg_data}(Значения метрик)'
            group_data = df[measure_names]
            r = {'agg_result':group_data}
            exec(f'agg_result = agg_result.{d[agg_data]}.to_frame().reset_index().rename(columns = {{"index":"Названия метрик", 0:"{y_data}"}})', r)
        else:
            group_data = df.groupby(x_data)[y_data]
            r = {'agg_result':group_data}
            exec(f'agg_result = agg_result.{d[agg_data]}.reset_index()', r)
            

        o = None
        if orientation:
            o = 'h'
            df_temp = r['agg_result'].sort_values(y_data, ascending = True)
            # for y_col in y_data:
            #     df_temp = df_temp.loc[~df_temp[y_col].isna()]

            if creation_top:
                df_temp = df_temp.tail(top_slider)
            x_data, y_data = y_data, x_data

        else:
            df_temp = r['agg_result'].sort_values(y_data, ascending = False)

            if creation_top:
                df_temp = df_temp[:top_slider]
        
        bm = 'stack' if barmode else 'group'
        bar_fig = px.bar(df_temp, x=x_data, y=y_data, barmode = bm, orientation = o, template = template)
        bar_fig.update_layout(
            title={
                'text': barchart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
            }
        )
        return dcc.Graph(figure=bar_fig)