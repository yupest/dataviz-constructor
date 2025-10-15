from dash import dcc, html, Output, Input, State, dash_table, no_update, ctx
import pandas as pd
import json
import base64
import io
import dash_bootstrap_components as dbc
from dash.dependencies import ALL

# TODO: переместить стилевые константы в отдельный файл(ы)
P_STYLE = {
     'margin-top': 10,
     'margin-bottom': 5
}

tab_style = {
    'padding': '10px 10px',  # Универсальные отступы
    'display': 'flex',
    'alignItems': 'center',  # Вертикальное выравнивание содержимого
    'justifyContent': 'center',  # Горизонтальное выравнивание
    'textAlign': 'center',
}

drop_sheet = dcc.Tab(id = {'index':'drop', 'type':'sheet'}, label = '❌', value = 'drop', style = tab_style, selected_style=tab_style)
append_sheet = dcc.Tab(id = {'index':'add', 'type':'sheet'}, label = '➕', value = 'add', style = tab_style, selected_style=tab_style)

BTN_style = {'margin':'10px 0px 5px 2px',
             'backgroundImage':'url("https://github.com/yupest/nto/blob/master/src/{btn}.png?raw=true")',
             'backgroundRepeat': 'no-repeat',
             'backgroundPosition': '10px center',
             'backgroundSize': '20px',
             'padding':'0px 10px 0px 35px',
             'textAlign': 'right'}

def get_btn_style(url):
    d = BTN_style.copy()
    d['backgroundImage'] = d['backgroundImage'].format(btn = url)
    return d

def parse_contents(contents, filename):
    df_uploaded = pd.DataFrame()

    if contents:
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            if 'csv' in filename:
                df_uploaded = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                df_uploaded = pd.read_excel(io.BytesIO(decoded))
            elif 'json' in filename:
                df_uploaded = pd.read_json(io.StringIO(decoded.decode('utf-8')))

        except Exception as e:
            print(f'parse content for {filename}', e)

    return df_uploaded

def register_data_callbacks(app):
    ######################################## processing the data ########################################
    @app.callback(
          [Output('raw-data', 'data'),
           Output('storage', 'data', allow_duplicate=True)],
           Input('upload-data', 'contents'),  # Триггер
           State('upload-data', 'filename'),  # Дополнительные данные
           prevent_initial_call=True
    )
    def set_data(contents, filename):
        # print('--------------------set_data------------------')
        json_data = {
            'filename': filename,
            'data': '[]',
            'hidden_columns': []
        }
        if not contents:
            # print('contents')
            return json_data, None
            # raise PreventUpdate
        try:
            df = parse_contents(contents, filename)
            cols_exist = df.columns.to_list()
            # print(cols_exist)
            df['NA'] = (df.isna().any(axis=1) | (df == '').any(axis=1)).astype(int)
            df = df[['NA']+cols_exist]
            json_data['data'] = df.to_json(orient='records')
        except Exception as e:
            print(f"Error: {e}")
        # print('data: ', json_data['data'][:50])
        return json_data, None
    
    ######################################## processing the data table ########################################
    @app.callback(Output('data-file', 'data', allow_duplicate=True),
              Output('menu-data', 'children'),
              Input('raw-data', 'data'),
              State('data-file', 'data'),
              prevent_initial_call=True)
    def get_table(raw_data, data):
        if not raw_data:return no_update, no_update
        if not data or isinstance(data, str) or data['data']=='[]' or data['filename']!= raw_data['filename']:
            data = raw_data
        if data['data']!='[]':
            menu = [html.H3(data['filename'], style = {'text-align': 'center','margin-top': 15}),
                    html.Div([html.Button('Данные', id = 'show-data-btn', style = get_btn_style('datatable')),
                              html.Button('Статистика', id = 'show-describe-btn', style = get_btn_style('describe')),
                              dcc.Input(type = 'text', placeholder = 'Название файла', id = 'input-filename',style={
                                        'margin': '10px 0px 11.5px 2px',
                                        'height': '38px',  # Примерная высота кнопок
                                        'border': '1px solid #ccc',
                                        'borderRadius': '4px',
                                        'fontSize': '14px',
                                        'verticalAlign': 'middle'
                                    }),
                              html.Button('Энкодер', id = 'encoder-btn', style = get_btn_style('encode')),
                              html.Button('Скачать данные', id = 'download-data-btn', style = get_btn_style('download'))],
                             style = {'text-align':'right', 'position': 'absolute','width': '75%','z-index': '1','margin-left': '25%'})]

            return data, menu

        else:
            return raw_data, [html.P('Не удалось прочитать файл. Проверьте формат файла, доступны: xls, xlsx, csv, json.', style=P_STYLE)]


    @app.callback(Output('show-data', 'hidden', allow_duplicate=True),
              Output('show-describe', 'hidden', allow_duplicate=True),
              Input('show-describe-btn', 'n_clicks'),
              Input('show-data-btn', 'n_clicks'),
              # State('df-table', 'data'),
              prevent_initial_call=True)
    def set_visible(show_describe, show_data):
        # print('show data or describe')
        if 'show-describe-btn' == ctx.triggered_id:
            return True, False
        else:
            return False, True

    @app.callback(Output('df-table', 'hidden_columns'),
              Input('df-table', 'hidden_columns'),
              State('data-file', 'data'))
    def change_hidden_columns(hidden_columns, data):
        if data['data']!='[]':
            df = pd.read_json(data['data'], orient='records')
            return list(set(hidden_columns)& set(df.columns)) if hidden_columns else []
        return no_update

    @app.callback(Output('output-datatable', 'children'),
              Input('data-file', 'data'))
    def show_table(data):
        # print('show_table')
        # print(data['hidden_columns'])

        if data['data']!='[]':
            print('data not is empty')
            dataset =  json.loads(data['data'])
            df = pd.read_json(data['data'], orient='records')

            # print(df.head(1))
            styles = [{
                'if': {
                    'column_id': 'NA'
                },
                'backgroundColor': '#FFE4B5'
            }]
            df_table = dash_table.DataTable(
                        id = 'df-table',
                        data = dataset,
                        columns=[{'name': i,
                                  'id': i,
                                  'type':'text' if df[i].dtype=='object' else 'numeric',
                                  'validation':{'default':'' if df[i].dtype=='object' else None},
                                  'on_change': {'failure': 'default'},
                                  'hideable': True,
                                  'renamable': True}
                                 for i in df.columns],
                        style_table={'overflowX': 'auto'},
                        style_data_conditional = styles+[
                            {
                                'if': {
                                    'filter_query': '{{{}}} is blank'.format(col),
                                    'column_id': col
                                },
                                'backgroundColor': 'tomato',
                                'color': 'white'
                            } for col in df.columns
                        ],
                        editable=True,
                        hidden_columns = data['hidden_columns'],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        column_selectable="single",
                        row_selectable="multi",
                        row_deletable=True,
                        selected_columns=[],
                        selected_rows=[],
                        page_action="native",
                        page_current= 0,
                        page_size=15,
                        persistence = True,
                        persistence_type='local',
                        persisted_props = ['hidden_columns', 'filter_query', 'page_current', 'selected_columns', 'selected_rows'],
                        style_header={
                            'textAlign': 'center',  # Центрируем заголовки
                            'backgroundColor': 'white',
                            'fontWeight': 'bold'
                        },
                        css = [{'selector':'.dash-spreadsheet-container',
                               'rule':'''margin-top: 5px;'''},
                               {'selector':'.show-hide',
                                'rule':'''font-size: 0;
                                        margin:10px 0px 5px 2px;
                                        background-image:url("https://github.com/yupest/nto/blob/master/src/hide.png?raw=true") !important;
                                        background-repeat: no-repeat;
                                        background-position: 10px center;
                                        background-size: 20px;
                                        padding-left: 0px !important;
                                '''},
                               {'selector':'.show-hide::after',
                                'rule':'''content: "Скрыть/Показать поля";
                                          font-size: 11px;
                                          margin-left:2px;
                                          padding-left: 35px !important;

                                '''},
                               {'selector':'input[type=checkbox]',
                                'rule':'''margin-right: 5px;'''},
                               ]
                    )
            object_list = []
            discrete_list = []
            num_list = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    object_list.append(col)
                elif df[col].dtype == 'int64' and len(df[col].unique())<50:
                    discrete_list.append(col)
                else:
                    num_list.append(col)

            style_num_columns = [{
                'if': {'column_id': i},
                'backgroundColor': 'white',
                'color':'Green',
                'fontWeight': 'bold'
            } for i in num_list]
            style_discrete_columns = [{
                'if': {'column_id': i},
                'backgroundColor': 'white',
                'color':'Orange',
                'fontWeight': 'bold'
            } for i in discrete_list]
            style_object_columns = [{
                'if': {'column_id': i},
                'backgroundColor': 'white',
                'color':'Blue',
                'fontWeight': 'bold'
            } for i in object_list]

            df_copy = df.copy()
            df_copy[discrete_list] = df_copy[discrete_list].astype('object')
            df_copy[object_list+discrete_list].describe()

            df_desc = df[num_list+discrete_list].describe().reset_index()
            dataset =  json.loads(df_desc.to_json(orient = 'records'))

            df_describe = dash_table.DataTable(
                            id = 'df-table-describe',
                            data = dataset,
                            columns=[{'name': i, 'id': i} for i in df_desc.columns],
                            style_table={'overflowX': 'auto'},
                            editable=False,
                            persistence_type='local',
                            style_header={
                                'textAlign': 'center',  # Центрируем заголовки
                                'backgroundColor': 'white',
                                'fontWeight': 'bold'
                            },
                            style_header_conditional=style_num_columns+style_discrete_columns,
                            style_data_conditional=[{
                                'if': {'column_id': 'index'},
                                'backgroundColor': 'white',
                                'fontWeight': 'bold'
                            }],
                            css = [{'selector':'.dash-spreadsheet-container',
                                   'rule':'''margin-top: 0px;'''}]
                        )

            df_desc = df_copy[object_list+discrete_list].describe().reset_index()
            dataset =  json.loads(df_desc.to_json(orient = 'records'))

            df_describe_object = dash_table.DataTable(
                            id = 'df-table-describe_object',
                            data = dataset,
                            columns=[{'name': i,'id': i} for i in df_desc.columns],
                            style_table={'overflowX': 'auto'},
                            editable=False,
                            persistence_type='local',
                            style_header={
                                'textAlign': 'center',  # Центрируем заголовки
                                'backgroundColor': 'white',
                                'fontWeight': 'bold'
                            },
                            style_header_conditional=style_object_columns+style_discrete_columns,
                            style_data_conditional=[{
                                'if': {'column_id': 'index'},
                                'backgroundColor': 'white',
                                'fontWeight': 'bold'
                            }],
                            css = [{'selector':'.dash-spreadsheet-container',
                                   'rule':'''margin-top: 0px;'''}]
                        )
            variables = [html.P(children = [html.B(' 🟩 Непрерывные '), '– числовые величины, которые используются в вычислениях (агрегируются).'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' 🟧 Дискретные '),'– величины целочисленного типа, которые могут быть представлены как категории, так и числовыми величинми, имеют ограниченный ряд. Например: год, часы, размер вещей и др.'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' 🟦 Номинальные'),' – категориальные переменные, имеют текстовый тип данных и чаще всего, используются для группировки вычислений.'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' count '), '– сколько всего не пустых записей в столбце'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' mean '), '– среднее значение (все числа сложили и разделили на количество).'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' std '), '– стандартное отклонение. Показывает насколько сильно числа отличаются от среднего (чем больше, тем сильнее разброс).'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' min '), '– минимальное значение в столбце'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' 25% '), '– четверть чисел меньше этого значения (нижняя граница большинства чисел)'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' 50% '), '– середина всех чисел (половина чисел меньше, половина - больше)'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' 75% '), '– три четверти чисел меньше этого значения (верхняя граница большинства чисел)'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' max '), '– максимальное значение в столбце'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' unique '), '– количество уникальных значений (показывает сколько разных неповторяющихся значений есть в столбце)'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' top '), '– какое значение встречается чаще всего'], style = {'textAlign':'left'}),
                        html.P(children = [html.B(' freq '), '– сколько раз встретилось самое частое значение'], style = {'textAlign':'left'}),
                        ]

            return [html.Div(id = 'show-data', children = df_table, hidden = False),
                    html.Div(id = 'show-describe', children = [html.P('Числовые переменные', style = {'fontWeight':'bold',  'font-size':'12pt', 'margin-top':'10px'}),
                                                               df_describe,
                                                               html.P('Категориальные переменные', style = {'fontWeight':'bold',  'font-size':'12pt', 'margin-top':'10px'}),
                                                               df_describe_object,
                                                               html.P('Обозначения', style = {'fontWeight':'bold',  'font-size':'12pt', 'margin-top':'10px'})]+variables, hidden = True, style = {'margin-top': '58px'})]
        else:
            print('data is empty')
            return []

    @app.callback(Output('download-data', 'data'),
              Input('download-data-btn', 'n_clicks'),
              Input('encoder-btn', 'n_clicks'),
              State('df-table', 'hidden_columns'),
              State('df-table', 'derived_virtual_data'),
              State('raw-data', 'data'),
              State('input-filename', 'value'),
              prevent_initial_call=True)
    def download_data(download_btn, encode_btn, hidden_columns, data, raw_data, filename):
        if not hidden_columns:
            hidden_columns = []
        if download_btn or encode_btn:
            # print(hidden_columns)
            df = pd.read_json(json.dumps(data)).drop(columns = ['NA']+hidden_columns)
            new = '_new.'
            if 'encoder-btn' == ctx.triggered_id:
                for col in df.columns:
                    if df[col].dtype=='object':
                        df[col] = df[col].astype('category').cat.codes
                new = '_encode.'
            name_list = raw_data['filename'].split('.')
            if filename:
                name = filename
            else:
                name = '.'.join(name_list[:-1])
            format_file = name_list[-1]
            return dcc.send_data_frame(df.to_csv, name+new+format_file, index = False)
        else:
            return no_update

    @app.callback(Output('data-file', 'data', allow_duplicate=True),
              Input('df-table', 'data'),
              State('df-table', 'hidden_columns'),
              # Input('show-data-btn', 'n_clicks'),
              State('raw-data', 'data'),
              prevent_initial_call = True)
    def set_table(new_data, hidden_columns, data):
        print('new_data\n', new_data)
        if new_data and new_data!=[]:
            if 'is_null' in hidden_columns:
                hidden_columns.remove('is_null')
                data['hidden_columns'] = hidden_columns
            # print('set_table')
            df = pd.read_json(json.dumps(new_data))
            print(df.columns)
            df['NA'] = (df.isna().any(axis=1) | (df == '').any(axis=1)).astype(int)
            data['data'] = df.to_json(orient='records')
            return data
        else:
            no_update

    type_diagrams = {'bar':'Столбчатая', 'line':'Линейная', 'dot':"Точечная", 'table':'Цветная таблица', 'pie':"Круговая", 'text':"Текст", 'wordcloud':"Облако слов"}
    icons = [{'label': html.Span([
                        html.Img(src=f"https://github.com/yupest/nto/blob/master/src/{k}.png?raw=true", height=25),
                        html.Span(v, style={ 'padding-left': 10})],
                       style={'align-items': 'center', 'justify-content': 'center'}),
              'value': k}  for k, v in type_diagrams.items()]

    @app.callback(
        Output("drop_sheets", "n_clicks"),
        Input("storage", "data"),
        prevent_initial_call=True
    )
    def reset_drop_clicks(_):
        # всегда обнуляем после обновления tabs/storage
        return 0

    # При загрузке страницы читаем данные из хранилища
    @app.callback(
        Output("tabs", "children"),
        Output("tabs", "value"),
        Output("storage", "data"),
        Output('dashboard-items', 'children'),
        Input("storage", "data"),
        Input('drop_sheets', 'n_clicks'),
        prevent_initial_call=False
    )
    def load_tabs(stored_data, n_clicks):
        # print(n_clicks)
        if not stored_data or n_clicks:
            # Первый запуск — создаем лист по умолчанию
            tab = dcc.Tab(id = {'index':'sheet_1', 'type':'sheet'}, label = 'Лист 1', value = 'Лист 1', children = [

                    dbc.Container([dcc.Dropdown(
                        id = {'index':"sheet_1", 'type':'chart_type'}, placeholder = 'Выберите тип диаграммы',
                        persistence='local',
                        options=icons)], style = {'margin-top':10}, fluid=True),
                    dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                html.Div(id={'index':'sheet_1', 'type' :'menu'})
                            ], width={'size':4}),

                            dbc.Col([
                                dcc.Loading(html.Div(id = {'index':'sheet_1', 'type' : 'chart'}, style = {'text-align':'center'}) , type="circle", style={"visibility":"visible", "filter": "blur(2px)", 'margin-top':'100px'})
                            ], width={'size':8})

                        ]),
                    ], fluid=True)
                    ], style = tab_style, selected_style=tab_style)

            default_data = {"sheets": {'Лист 1': tab}, "active_tab": "Лист 1"}
            dashboard = html.Div(id={'index':"sheet_1", 'type':'dashboard'},
                     style={
                        "height":'100%',
                        "width":'100%',
                        "display":"flex",
                        "flex-direction":"column",
                        "flex-grow":"0"
                    })
            return [tab, append_sheet, drop_sheet], "Лист 1", default_data, [dashboard]
        else:
            # Восстанавливаем из хранилища
            tabs = [tab for tab in stored_data["sheets"].values()]
            tabs.append(append_sheet)
            tabs.append(drop_sheet)

            dashboard = [html.Div(id={'index':"sheet_"+ind.split(' ')[-1], 'type':'dashboard'}, style={
                            "height":'100%',
                            "width":'100%',
                            "display":"flex",
                            "flex-direction":"column",
                            "flex-grow":"0"
                        }) for ind in stored_data["sheets"].keys() ]

            return tabs, stored_data["active_tab"], no_update, dashboard

    @app.callback(
        Output("storage", "data", allow_duplicate=True),
        Output("confirm-delete", "displayed"),
        Output("confirm-delete", "message"),
        Input('tabs', 'value'),
        Input('tabs', 'children'),
        Input({'index': ALL, 'type':'menu'}, 'children'),
        Input({"index": ALL, "type": "sheet"}, 'label'),
        Input({'index':ALL, 'type':'top-slider-bar'}, 'value'),
        State("storage", "data"),
        prevent_initial_call=True
    )
    def set_active_tab(active_tab, tabs, menu, label, top, stored_data):
        # print('active_tab: ', ctx.triggered_id)
        if active_tab!='drop' and active_tab != 'add':
            stored_data['active_tab'] = active_tab
            stored_data["sheets"] = {tab['props']['value']: tab for i, tab in enumerate(tabs[:-2])}
        elif active_tab=='add':
            if len(stored_data['sheets'])<10:
                number_tab = max([int(sheet.split()[1]) for sheet in stored_data['sheets'].keys()])+1
                # print('max_sheet', number_tab)
                new_tab_name = f"Лист {number_tab}"

                new_tab = dcc.Tab(label=new_tab_name, value=new_tab_name, id = {'index':f'sheet_{number_tab}', 'type':'sheet'}, children = [
                                dbc.Container([dcc.Dropdown( id= {'index':f'sheet_{number_tab}', 'type' : 'chart_type'}, placeholder = 'Выберите тип диаграммы',
                                                            persistence='local', options=icons)],
                                              style = {'margin-top':10}, fluid=True),
                                dbc.Container([
                                    dbc.Row([
                                        dbc.Col([
                                            html.Div(id = {'index':f'sheet_{number_tab}', 'type' : 'menu'})
                                        ], width={'size':4}),

                                        dbc.Col([
                                            dcc.Loading(html.Div(id = {'index':f'sheet_{number_tab}', 'type' : 'chart'}, style = {'text-align':'center'}) , type="circle", style={"visibility":"visible", "filter": "blur(2px)", 'margin-top':'100px'})
                                        ], width={'size':8})

                                    ]),
                                ], fluid=True)
                    ], style = tab_style, selected_style=tab_style)

                tabs = tabs[:-2] + [new_tab]
                # print(tabs[0]['props']['value'])
                for tab in tabs[:-2]:
                    stored_data["sheets"][tab['props']['value']] = tab
                stored_data["sheets"][new_tab_name] = new_tab
                stored_data["active_tab"] = new_tab_name
                # print(stored_data)

        else:
            return no_update, True, f'Вы уверены, что хотите удалить "{stored_data["active_tab"]}"?'
        return stored_data, no_update, no_update

    @app.callback(
        Output("storage", "data", allow_duplicate=True),
        Input("confirm-delete", "submit_n_clicks"),
        State('storage', 'data'),
        prevent_initial_call=True
    )
    def show_confirmation(n_clicks, stored_data):
        # print(stored_data['active_tab'])
        number_sheets = len(stored_data['sheets'])
        if n_clicks:
            if number_sheets == 1:
                return None
            active_tab = stored_data['active_tab']
            del stored_data["sheets"][active_tab]
            active_tab = list(stored_data["sheets"].keys())[-1]
            stored_data['active_tab'] = active_tab
            return stored_data
        return no_update