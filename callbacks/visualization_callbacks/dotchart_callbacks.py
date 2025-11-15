from dash import dcc, Input, Output, State, no_update
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

def register_dotchart_callbacks(app):
    @app.callback(Output({'index':MATCH, 'type':'sheet'},'label', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'style', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'selected_style', allow_duplicate=True),
              Input({'index':MATCH, 'type':'name-dot'},'value'),
              prevent_initial_call=True)
    def rename_sheet_dot(name):
        style = {**tab_style, **custom_style_tab, 'background-image':"url('https://github.com/yupest/nto/blob/master/src/dot.png?raw=true')"}
        if not name:
            return no_update, style, style
        else:

            return name, style, style

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
                
                Input({'index':MATCH, 'type':'xaxis'},'value'),
                Input({'index':MATCH, 'type':'yaxis'}, 'value'),
                Input({'index':MATCH, 'type':'tooltip-dot'}, 'value'),
                Input({'index':MATCH, 'type':'show-line-dot'},'value'),
                Input({'index':MATCH, 'type':'size-dot'}, 'value'),
                Input({'index':MATCH, 'type':'size-column-dot'}, 'value'),
                Input({'index':MATCH, 'type':'color-dot'}, 'value'),
                Input({'index':MATCH, 'type':'opacity-dot'}, 'value'),
                Input({'index':MATCH, 'type':'name-dot'},'value'),
                Input({'index':MATCH, 'type':'sheet'}, 'value'),
                State('storage','data'),
                prevent_initial_call=True)

    def make_scatter(x_data, y_data, tooltip, show_line, size_dot, size_data, color_data, opacity, dotchart_name, sheet, storage):
        data = storage['data']['df']
        hidden_columns = storage['data']['hidden_columns']
        
        df = pd.read_json(data, orient='records')
        cols = ['NA'] if 'NA' in df.columns else []
        cols += hidden_columns if hidden_columns else []
        df = df.drop(columns = cols)


        cols = tooltip if tooltip else []
        for i in [x_data, y_data, color_data]:
            if not pd.isna(i):
                cols.append(i)
                df = df.loc[~df[i].isna()]
        # if cols!=[]:
        #     df = df.groupby(cols)[[x for x in [x_data, y_data, size_data] if x is not None]].mean().reset_index()
        dot_fig = px.scatter(df, x=x_data, y=y_data, size=size_data, hover_data=cols,
                             color_discrete_sequence=px.colors.qualitative.Plotly, color=color_data, opacity = opacity/100)
        dot_fig.update_layout(
            title={
                'text': dotchart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            })

        # print(size_data)
        if not size_data:
            dot_fig.update_traces(marker_size=size_dot)

        print('show_line', show_line)
        if show_line:
            print(color_data)
            if color_data and df[color_data].dtype == 'object':
                items = [df.loc[df[color_data]==item] for item in df[color_data].unique()]
                colors = px.colors.qualitative.Plotly
            else:
                items = [df]
                colors = ['gray']
            for i, item in enumerate(items):
                X = item[x_data]
                Y = item[y_data]
                cov_matrix = np.cov(X, Y)
                a = cov_matrix[0, 1] / cov_matrix[0, 0]
                b = np.mean(Y) - a * np.mean(X)

                dot_fig.add_scatter(
                    x=np.linspace(min(X), max(X)),
                    y=a * np.linspace(min(X), max(X)) + b,
                    mode='lines',
                    name=f'y = {a:.3f}x + {b:.1f}',
                    hovertext = f'y = {a:.3f}x + {b:.1f}',
                    line=dict(color=colors[i])
                )
        return dcc.Graph(figure=dot_fig)
