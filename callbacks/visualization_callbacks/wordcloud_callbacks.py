from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dependencies import MATCH
from dash_holoniq_wordcloud import DashWordcloud
import pandas as pd
import json


def register_wordcloud_callbacks(app):

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
               Output({'index':MATCH, 'type':'frequency-slider-wordcloud'}, 'max', allow_duplicate=True),
                Input({'index':MATCH, 'type':'column-wordcloud'}, 'value'),
                Input({'index':MATCH, 'type':'explode-text-wordcloud'}, 'value'),
                Input({'index':MATCH, 'type':'count-wordcloud'}, 'value'),
                Input({'index':MATCH, 'type':'lenth-slider-wordcloud'}, 'value'),
                Input({'index':MATCH, 'type':'size-slider-wordcloud'}, 'value'),
                Input({'index':MATCH, 'type':'grid-slider-wordcloud'}, 'value'),
                Input({'index':MATCH, 'type':'color-wordcloud'}, 'value'),
                Input ({'index':MATCH, 'type':'frequency-slider-wordcloud'}, 'value'),
                Input({'index':MATCH, 'type':'sheet'}, 'value'),
                State('storage','data'),
                prevent_initial_call=True)
    def make_wordcloud(column, explode, column_count, sliderLength, slider_size, sliderGrid, wordsColor, frequency, sheet, storage):
        
        if not column:
            raise PreventUpdate
        
        security_data = []

        data = storage['data']['df']
        hidden_columns = storage['data']['hidden_columns']
        
        df = pd.read_json(json.dumps(data), orient='records')
        cols = ['NA'] if 'NA' in df.columns else []
        cols += hidden_columns if hidden_columns else []
        df = df.drop(columns = cols)
        
        if column_count:
            df = df[[column, column_count]].drop_duplicates()

        if explode:
            words = df[column].str.upper().str.extractall(r'([A-ZА-ЯЁ\d\-]+)').reset_index('match').rename(columns = {0:column})[column].to_frame()
        else:
            words = df[column].to_frame()
        words['lenth'] = words[column].apply(len)

        df_temp = words.loc[words['lenth']>=sliderLength, column].value_counts()
        mx, mn = df_temp.values.max(), df_temp.values.min()

        if mx==mn:
            security_data = [[k, x, k+' ('+str(x)+')'] for k, x in zip(df_temp.keys(), df_temp.values)]
        else:
            security_data = [[k, ((x-mn)/ (mx-mn))*(25)+5, k+' ('+str(x)+')'] for k, x in zip(df_temp.keys(), df_temp.values) if x >= frequency]

        cloud = DashWordcloud(
                id='wordcloud',
                list=security_data,
                width=800, height=500,
                gridSize=sliderGrid,
                weightFactor=slider_size,
                color=wordsColor['hex'],
                backgroundColor='#fff',
                shuffle=False,
                rotateRatio=0.5,
                ellipticity=1,
                hover=True
            )

        return cloud, security_data[0][1]