from dash import dcc, Input, Output, State, no_update
import plotly.express as px
from dash.dependencies import MATCH
import numpy as np
import pandas as pd

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
        return value, not_value


    @app.callback(Output({'index':MATCH, 'type':'value_filter-table'}, 'options'),
        Input({'index':MATCH, 'type':'filter-table'}, 'value'),
        State('storage','data'),
        prevent_initial_call=False)
    def set_options_table(filter_col, storage):
        data = storage['data']['df']
        df = pd.read_json(data, orient='records')
        
        if not filter_col:
            return no_update

        if filter_col == 'Названия метрик':
            return storage['data']['columns']['numeric']+storage['data']['columns']['discrete']
        
        return df[filter_col].unique()

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
        Input({'index':MATCH, 'type':'correlation'}, 'value'),
        Input({'index':MATCH, 'type':'xaxis-table'},'value'),
        Input({'index':MATCH, 'type':'yaxis-table'}, 'value'),
        Input({'index':MATCH, 'type':'zaxis-table'}, 'value'),
        Input({'index':MATCH, 'type':'correlation-type-table'}, 'value'),
        Input({'index':MATCH, 'type':'agg-table'}, 'value'),
        Input({'index':MATCH, 'type':'filter-table'}, 'value'),
        Input({'index':MATCH, 'type':'value_filter-table'}, 'value'),
        Input({'index':MATCH, 'type':'name-chart'},'value'),
        Input({'index':MATCH, 'type':'sheet'}, 'value'),
        Input('template', 'value'),
        State('storage','data'),
        prevent_initial_call=True)
    def make_table(correlation, x_data, y_data, z_data, corr_type, agg_data, filter_col, value_filter, chart_name, sheet, template, storage):
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

        if correlation:
            cols = df.columns[np.array([df[i].dtype != 'object' for i in df.columns])].tolist()
            table_chart = px.imshow(df[cols].corr(corr_type).round(3), text_auto=True, aspect="auto", template = template)

        else:
            ### dictionary for an aggregation ###
            d = {'sum': 'sum()', 'avg':'mean()', 'count': 'count()', 'countd': 'nunique()', 'min':'min()', 'max':'max()'}

            if not all([x_data, y_data, z_data]) and x_data==y_data:
                return []

            if y_data == 'Названия метрик':
                x_data, y_data = y_data, x_data

            if x_data == 'Названия метрик' and z_data == 'Значения метрик':
                group_data = df.groupby(y_data)[measure_names]
                r = {'agg_result':group_data}
                exec(f'agg_result = agg_result.{d[agg_data]}', r)
                df_temp = r['agg_result']
                df_temp.index = df_temp.index.astype('str')
            else:
                df[[x_data, y_data]] = df[[x_data, y_data]].astype(str)
                group_data = df.groupby([x_data, y_data])[z_data]
                r = {'agg_result':group_data}
                exec('agg_result = agg_result.'+d[agg_data], r)

                df_temp = r['agg_result'].reset_index().pivot(index=x_data, columns=y_data, values=z_data)

            table_chart = px.imshow(df_temp.round(3), text_auto=True, zmax = df_temp.stack().quantile(0.75), zmin = df_temp.min().min(), aspect="auto", template = template)

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