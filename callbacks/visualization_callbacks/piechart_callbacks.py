from dash import dcc, Input, Output, State, no_update
import plotly.express as px
from dash.dependencies import MATCH
import pandas as pd

def register_piechart_callbacks(app):

    @app.callback(Output({'index':MATCH, 'type':'value_filter-pie'}, 'options'),
              Input({'index':MATCH, 'type':'filter-pie'}, 'value'),
              State('storage','data'),
              prevent_initial_call=False)
    def set_options_pie(filter_col, storage):
        data = storage['data']['df']
        df = pd.read_json(data, orient='records')
        if not filter_col:
            return no_update
        if filter_col == 'Названия метрик':
            return storage['data']['columns']['numeric']+storage['data']['columns']['discrete']
        
        return df[filter_col].unique()

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
               Input({'index':MATCH, 'type':'xaxis'},'value'),
               Input({'index':MATCH, 'type':'yaxis'}, 'value'),
               Input({'index':MATCH, 'type':'sectors-slider'}, 'value'),
               Input({'index':MATCH, 'type':'agg-pie'}, 'value'),
               Input({'index':MATCH, 'type':'filter-pie'}, 'value'),
               Input({'index':MATCH, 'type':'value_filter-pie'}, 'value'),
               Input({'index':MATCH, 'type':'name-chart'},'value'),
               Input({'index':MATCH, 'type':'sheet'}, 'value'),
               Input('template', 'value'),
               State('storage','data'),
              prevent_initial_call=True)
    def make_pie(x_data, y_data, sliderSectors, agg_data, filter_col, value_filter, piechart_name, sheet, template, storage):
        
        if not x_data or not y_data:
            return []
        
        data = storage['data']['df']
        hidden_columns = storage['data']['hidden_columns']
        
        df = pd.read_json(data, orient='records')
        
        d = {'sum': 'sum()', 'avg':'mean()', 'count': 'count()', 'countd': 'nunique()', 'min':'min()', 'max':'max()'}
        
        cols = ['NA'] if 'NA' in df.columns else []
        cols += hidden_columns if hidden_columns else []
        df = df.drop(columns = cols)

        measure_names = storage['data']['columns']['numeric']+storage['data']['columns']['discrete']
        if filter_col and value_filter:
            if filter_col == 'Названия метрик':
                measure_names = value_filter
            else:
                df = df.loc[df[filter_col].isin(value_filter)]

        if x_data == 'Названия метрик' and y_data == 'Значения метрик':
            y_data = f'{agg_data}(Значения метрик)'
            group_data = df[measure_names]
            r = {'agg_result':group_data}
            exec(f'agg_result = agg_result.{d[agg_data]}.to_frame().reset_index().rename(columns = {{"index":"Названия метрик", 0:"{y_data}"}})', r)
        else:
            group_data = df.groupby(x_data)[y_data]
            r = {'agg_result':group_data}
            exec(f'agg_result = agg_result.{d[agg_data]}.reset_index()', r)
            

        df_temp = r['agg_result']

        if df_temp.shape[0] > sliderSectors:
             df_temp = df_temp.sort_values(y_data, ascending = False).reset_index()
             df_temp.loc[sliderSectors:, x_data] = 'Другое'
             df_temp = df_temp.groupby(x_data).sum()

        pie_fig = px.pie(df_temp, values=y_data, names=x_data, color_discrete_sequence=px.colors.qualitative.Plotly, template = template)
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
