from dash import Dash, dcc, html, Input, Output, State, callback, dash_table, no_update, ctx
from dash.exceptions import PreventUpdate
import dash_draggable
import pandas as pd
import json
from dash.dependencies import MATCH, ALL
import dash_bootstrap_components as dbc
import dash_daq as daq
import uuid
from callbacks import register_all_callbacks

INPUT_STYLE = {
     'width': '100%'
}

P_STYLE = {
     'margin-top': 10,
     'margin-bottom': 5
}
tabs_styles = {
    'height': 'auto',  # Автоматическая высота
}

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

style_btn_dashboard = get_btn_style('download')
style_btn_dashboard['width'] = '100%'
app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN, 'https://codepen.io/chriddyp/pen/bWLwgP.css' ], suppress_callback_exceptions=True)
server = app.server
drop_sheet = dcc.Tab(id = {'index':'drop', 'type':'sheet'}, label = '❌', value = 'drop', style = tab_style, selected_style=tab_style)
append_sheet = dcc.Tab(id = {'index':'add', 'type':'sheet'}, label = '➕', value = 'add', style = tab_style, selected_style=tab_style)


app.layout = html.Div([
    dcc.Store(id="storage", storage_type="local"),
    dcc.Store(id="essay-order", storage_type="local", data=[]),  # Хранилище порядка листов для эссе
    
    dbc.Row([
        # Лого ИГУ (левое)
        dbc.Col([
            html.Div([
                # html.Img(src='https://github.com/yupest/nto/blob/master/src/vis.png?raw=true', style={'width': '15%'}),
                html.Img(
                    src='https://isu.ru/export/sites/isu/ru/media/.galleries/images/isu_black.png',
                    style={'width': '45%'}
                )
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'justifyContent': 'flex-start',
                'height': '100%'
            })
        ], width=3, style={'padding-left': '14px'}),

        # Центральный заголовок
        dbc.Col([
            html.Div([

                html.H1("Датавиз-конструктор", style={'margin': '0 0 0 10px'})
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'justifyContent': 'center',
                'height': '100%'
            })
        ], width=6),

        # Лого RSV (правое)
        dbc.Col([
            html.Div([
                html.Img(
                    src='https://static.tildacdn.com/tild6231-6235-4131-b239-313435643830/rsv_ntojunior_2024.svg',
                    style={'width': '80%'}
                )
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'flex-end',
                'height': '100%'
            })
        ], width=3, style={'padding-right': '14px'})
    ], align='center', style={'height': '100%', 'margin-top':'5px', 'margin-bottom':'5px'}),
    dcc.Tabs([dcc.Tab(label='Данные', children = [
            dbc.Container([
            dcc.Store(id='raw-data', storage_type = 'local', data = {'filename': '', 'data': '[]', 'hidden_columns': []}),
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Перетащите или ', html.A('выберите файл')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin-top': '10px'
                },
                multiple=False,

            ),
            dcc.Download(id="download-data"),
            dcc.Loading(
                # [dbc.Alert("My Data", id="loading-overlay-output", className="h4 p-4 mt-3")],
                [dcc.Store(id='data-file', storage_type='local', data = {'filename': '', 'data': '[]', 'hidden_columns':[]}),
                html.Div(id='menu-data'),
                html.Div(id='output-datatable', style={
                    'width': '100%',
                    # 'height': '60px',
                    'textAlign': 'center',
                    'margin-top': '10px'
                })],

                style={"visibility":"visible", "filter": "blur(2px)"},
                type="circle",
            ),

        ], fluid=True)], style = tab_style, selected_style=tab_style),

        dcc.Tab(label='Визуализация',children = [

            dcc.Tabs(id = 'tabs', value = 'Лист 1', style = tabs_styles),
            html.Button("Удалить все листы", id="drop_sheets", style = {'display':'none'}),
            dcc.ConfirmDialog(
                id="confirm-delete",
            )

        ], style = tab_style, selected_style=tab_style),
        dcc.Tab(label='Дашборд', id = 'tab-dashboard', children = [
            dbc.Container(dbc.Row([dbc.Col(dcc.Input(id = 'input-name-dashboard',type = 'text',
                                                     placeholder = 'Введите название Дашборда',
                                                     style = {'width': '100%','margin': '10px 0px 5px 0px','font-size': '20pt','font-weight': 'bold', 'border':'none'},
                                                     persistence='local'), width = 10),
                                   dbc.Col(html.Button('Скачать html-дашборд', id='save-html', n_clicks=0, style = style_btn_dashboard), width = 2, style = {'text-align':'right'})
                           ]),
                          style = {'margin-top':10}, fluid=True),
            html.Div(id = 'dashboard', children = [
                dash_draggable.ResponsiveGridLayout(id = 'dashboard-items',gridCols = {'lg': 16, 'md': 12, 'sm': 8, 'xs': 4, 'xxs': 2})]
            ),
            dcc.Download(id="download-html")
        ], style = tab_style, selected_style=tab_style),
        
        # НОВАЯ ВКЛАДКА - ВЫЧИСЛИТЕЛЬНОЕ ЭССЕ
        dcc.Tab(label='Вычислительное эссе', id='tab-essay', children=[
            dbc.Container(dbc.Row([
                dbc.Col(dcc.Input(id='input-name-essay', type='text',
                                 placeholder='Введите название эссе',
                                 style={'width': '100%','margin': '10px 0px 5px 0px','font-size': '20pt','font-weight': 'bold', 'border':'none'},
                                 persistence='local'), width=10),
                dbc.Col(html.Button('Скачать html-эссе', id='save-essay', n_clicks=0, style=style_btn_dashboard), width=2, style={'text-align':'right'})
            ]), style={'margin-top':10}, fluid=True),
            
            dbc.Row([
                # Левая панель - перетаскиваемый список листов
                dbc.Col([
                    html.H4("Порядок листов в эссе", style={'text-align': 'center', 'margin-bottom': '20px'}),
                    html.Div(id='essay-sortable-list', children=[
                        # Здесь будет генерироваться перетаскиваемый список
                    ], style={
                        'border': '1px solid #ddd',
                        'borderRadius': '5px',
                        'padding': '10px',
                        'minHeight': '400px',
                        'backgroundColor': '#f9f9f9'
                    }),
                    html.P("Перетащите листы для изменения порядка", 
                          style={'text-align': 'center', 'color': '#666', 'fontSize': '12px', 'marginTop': '10px'})
                ], width=3),
                
                # Правая панель - предпросмотр эссе
                dbc.Col([
                    html.H4("Предпросмотр эссе", style={'text-align': 'center', 'margin-bottom': '20px'}),
                    html.Div(id='essay-preview', style={
                        'border': '1px solid #ddd',
                        'borderRadius': '5px',
                        'padding': '20px',
                        'minHeight': '600px',
                        'backgroundColor': 'white',
                        'overflowY': 'auto'
                    })
                ], width=9)
            ]),
            dcc.Download(id="download-essay")
        ], style=tab_style, selected_style=tab_style),
        dcc.Tab(id = 'show-help',
                label = 'Справка', value = 'Справка',
                style = {**tab_style, **custom_style_tab, 'background-image':"url('https://github.com/yupest/nto/blob/master/src/help.png?raw=true')"},
                selected_style = {**tab_style, **custom_style_tab, 'background-image':"url('https://github.com/yupest/nto/blob/master/src/help.png?raw=true')"},
                children = dbc.Container([html.Br(),
                                          html.P('''С помощью платформы визуализации данных можно загружать, обрабатывать, анализировать и наглядно представлять информацию в виде графиков, диаграмм и интерактивных дашбордов.
                                                 Каждая вкладка предоставляет различный функционал по каждому этапу:'''),
                                          html.H5('Данные'),
                                          html.Button('Перетащите или выберите файл', style = {'margin':'10px 0px 5px 2px','disabled':True}), ' Загрузка данных в форматах .CSV, .JSON, .XLS, .XLSX',html.Br(),
                                          html.Button('Данные', style = {**get_btn_style('datatable'), 'disabled':True}), ' Просмотр данных: значения в таблице можно изменять, а колонки переименовывать',html.Br(),
                                          html.Button('Статистика', style = {**get_btn_style('describe'), 'disabled':True}), ' Просмотр описательной статистики',html.Br(),
                                          html.Button('Скрыть/Показать поля',  style = {**get_btn_style('hide'), 'disabled':True}), '', ' Скрытие и отображение колонок в данных', html.Br(),
                                          html.Button('NA',  style = {'margin':'10px 0px 5px 2px','disabled':True, 'background-color':'#FFE4B5'}), '', ' Поле в таблице для фильтрации пустых значений (1 - в строке есть пустые значения, 0 - нет)', html.Br(),
                                          html.Button('_', style = {'color':'#ff6347', 'width': '115px','margin':'10px 0px 5px 2px','disabled':True, 'background-color':'#ff6347'}), '', ' Пустое значение', html.Br(),
                                          html.Button('Энкодер',  style = {**get_btn_style('encode'), 'disabled':True}),' Скачивание данных с закодированными категориальными значениями через LabelEncoder (все категории становятся числами)', html.Br(),
                                          html.Button('Скачать данные', style = {**get_btn_style('download'), 'disabled':True}),' Скачивание данных ', html.Br(),
                                          'Скачивание данных и построение визуализаций производится с учетом скрытых колонок без поля ', html.Code('NA'), '. Настройка колонок опционально производится перед каждым созданием листа.',html.Br(),
                                          html.H5('Визуализация'),
                                          html.Button('Лист 1', style = {'margin':'10px 0px 5px 2px','disabled':True}), ' На листе настраивается одна визуализация: столбчатая, линейная, круговая, точечная диаграммы, облако слов, цветная таблица, текстовое поле.',html.Br(),
                                          html.Button('➕', style = {'margin':'10px 0px 5px 2px','disabled':True}), ' Добавление нового листа',html.Br(),
                                          html.Button('❌', style = {'margin':'10px 0px 5px 2px','disabled':True}), ' Удаление текущего листа', html.Br(),
                                          'Результат визуализации с каждого листа добавляется автоматически в дашборд',html.Br(),
                                          html.H5('Дашборд'),
                                          'Каждый блок с визуализацией можно перемещать за верхний край и масштабировать за левый нижний угол',html.Br(),
                                          html.Button('Скачать html-дашборд',  style = {**get_btn_style('download'), 'margin':'10px 0px 5px 2px','disabled':True}), ' Скачать дашборд в формате html: все визуализации (кроме облака слов) выгружаются в локальный файл.'
                                          ], fluid = True, style = {'width':'90%'}))
    ], style = tabs_styles)
])

register_all_callbacks(app)

######################################## processing the data table ########################################

@callback(Output('data-file', 'data', allow_duplicate=True),
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


@callback(Output('show-data', 'hidden', allow_duplicate=True),
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

@callback(Output('df-table', 'hidden_columns'),
          Input('df-table', 'hidden_columns'),
          State('data-file', 'data'))
def change_hidden_columns(hidden_columns, data):
    if data['data']!='[]':
        df = pd.read_json(data['data'], orient='records')
        return list(set(hidden_columns)& set(df.columns)) if hidden_columns else []
    return no_update

@callback(Output('output-datatable', 'children'),
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

@callback(Output('download-data', 'data'),
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

@callback(Output('data-file', 'data', allow_duplicate=True),
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

@callback(
    Output("drop_sheets", "n_clicks"),
    Input("storage", "data"),
    prevent_initial_call=True
)
def reset_drop_clicks(_):
    # всегда обнуляем после обновления tabs/storage
    return 0

# При загрузке страницы читаем данные из хранилища
@callback(
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

@callback(
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

@callback(
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


######################################## menu getter functions ########################################
# TODO: переместить эти функции в отдельный файл(ы)
def get_menu_bar(list_color_cols, ind):

    return [html.Div([
        html.P("Ось X", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'xaxis'},
                     options=[x['options'] for x in list_color_cols], persistence='local'),
        html.P("Ось Y", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'yaxis'},
                     options=[x['options'] for x in list_color_cols], multi=True, persistence='local'),
        html.P("Агрегация", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'agg-bar'},
                     options={
                         'sum': 'Сумма',
                         'avg': 'Среднее',
                         'count': 'Количество',
                         'countd':'Количество уникальных',
                         'min': 'Минимум',
                         'max': 'Максимум',
                         },
                     value='sum',
                     persistence='local'),
        dcc.Checklist(options = {'h':'Горизонтальная диаграмма'}, id = {'index':ind,'type':'orientation'}, persistence='local'),
        dcc.Checklist(options = {'top':'Создать топ'}, id = {'index':ind, 'type':'creation-top-bar'}, persistence='local'),
        dcc.Slider(min=1, max=20, step=1, value=20, id={'index':ind, 'type':'top-slider-bar'}, marks=None, disabled = True,
                    tooltip={"placement": "bottom", "always_visible": True}, persistence='local'),
        html.P("Фильтр", style = P_STYLE),
        dbc.Row([

                dbc.Col([dcc.Dropdown(id={'index':ind, 'type':'filter-bar'},
                             options=[x['options'] for x in list_color_cols if x['type']=='object' or x['type']=='discrete'], persistence='local')], width = 5),
                dbc.Col([html.P(" входит в ")], width = 2),
                dbc.Col([dcc.Dropdown(id={'index':ind, 'type':'value_filter-bar'}, multi = True, persistence='local')], width = 5),
            ]),
        html.P("Название графика", style = P_STYLE),
        dcc.Input(id={'index':ind, 'type':"name-bar"}, type="text", placeholder="Название", debounce=True, style = INPUT_STYLE, persistence='local'),

        ]
    )]

def get_menu_line(list_color_cols, ind):
    return [html.Div([
        html.P("Ось X", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'xaxis'},
                     options=[x['options'] for x in list_color_cols], persistence='local'),
        html.P("Ось Y", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'yaxis'},
                     options=[x['options'] for x in list_color_cols], multi=True, persistence='local'),
        html.P("Агрегация", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'agg-line'},
                     options={
                         'sum': 'Сумма',
                         'avg': 'Среднее',
                         'count': 'Количество',
                         'countd':'Количество уникальных',
                         'min': 'Минимум',
                         'max': 'Максимум',
                         },
                     value='sum',
                     persistence='local'),
        html.P("Фильтр", style = P_STYLE),
        dbc.Row([

                dbc.Col([dcc.Dropdown(id={'index':ind, 'type':'filter-line'},
                             options=[x['options'] for x in list_color_cols if x['type']=='object' or x['type']=='discrete'], persistence='local')], width = 5),
                dbc.Col([html.P(" входит в ")], width = 2),
                dbc.Col([dcc.Dropdown(id={'index':ind, 'type':'value_filter-line'}, multi = True, persistence='local')], width = 5),
            ]),
        html.P("Название графика", style = P_STYLE),
        dcc.Input(id={'index':ind, 'type':"name-line"}, type="text", placeholder="Название", style = INPUT_STYLE, persistence='local'),
        ]
    )]

def get_menu_wordcloud(list_color_cols, ind):
    return [html.Div([
                html.P("Текстовые данные", style = P_STYLE),
                dcc.Dropdown(id={'index':ind, 'type':'column-wordcloud'},
                            options=[x['options'] for x in list_color_cols if x['type']=='object'],
                            persistence='local'),
                dcc.Checklist(['Разбивать текст на слова'], id = {'index':ind, 'type':'explode-text-wordcloud'}, style = P_STYLE),

                html.P("Частота упоминаний слов:", style = P_STYLE),
                dcc.Dropdown(id={'index':ind, 'type':'count-wordcloud'},
                            options=[x['options'] for x in list_color_cols],
                            persistence='local'),
                html.P("Минимальная длина слова", style = P_STYLE),
                dcc.Slider(min=1, max=5, step=1, value=3, id={'index':ind, 'type':'lenth-slider-wordcloud'}, marks=None,
                            tooltip={"placement": "bottom", "always_visible": True}, persistence='local'),
                html.P("Частота упоминаний от", style = P_STYLE),
                dcc.Slider(min=1, max=10, step=1, value=3, id={'index':ind, 'type':'frequency-slider-wordcloud'}, marks=None,
                            tooltip={"placement": "bottom", "always_visible": True}, persistence='local'),
                html.P("Размер слов", style = P_STYLE),
                dcc.Slider(min=1, max=5, step=0.5, value=1, id={'index':ind, 'type':'size-slider-wordcloud'}, marks=None,
                            tooltip={"placement": "bottom", "always_visible": True}, persistence='local'),
                html.P("Масштаб сетки", style = P_STYLE),
                dcc.Slider(min=3, max=25, step=1, value=15, id={'index':ind, 'type':'grid-slider-wordcloud'}, marks=None,
                            tooltip={"placement": "bottom", "always_visible": True}, persistence='local'),
                html.P("Название листа", style = P_STYLE),
                dcc.Input(id={'index':ind, 'type':"name-wordcloud"}, type="text", placeholder="Название", style = INPUT_STYLE, persistence='local'),


                ]
            ),
            html.Div([
                html.P("Выберите цвет", style = P_STYLE),
                daq.ColorPicker(
                id={'index':ind, 'type':'color-wordcloud'},
                value=dict(hex='#000000'),
                persistence='local',
                style={'border':'0px'},
            )], style={'height':500, 'margin-top':10})
    ]

def get_menu_scatter(list_color_cols, ind):

    return [html.Div([
        html.P("Ось X", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'xaxis'},
                     options=[x['options'] for x in list_color_cols], persistence='local'),
        html.P("Ось Y", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'yaxis'},
                     options=[x['options'] for x in list_color_cols], persistence='local'),
        html.P("Подсказка при наведении", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'tooltip-dot'}, multi=True,
                     options=[x['options'] for x in list_color_cols], persistence='local'),
        dcc.Checklist(['Показать линию тренда'], id = {'index':ind, 'type':'show-line-dot'}, style = P_STYLE),
        html.P("Размер точек", style = P_STYLE),
        dcc.Slider(5, 30, 0,
               value=8,
               id={'index':ind, 'type':'size-dot'},
               ),
        dcc.Dropdown(id={'index':ind, 'type':'size-column-dot'},
                     options=[x['options'] for x in list_color_cols if x['type']!='object'], persistence='local'),
        html.P("Цвет точек", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'color-dot'},
                     options=[x['options'] for x in list_color_cols], persistence='local'),
        html.P("Прозрачность точек", style = P_STYLE),
        dcc.Slider(0, 100, 0,
               value=50,
               id={'index':ind, 'type':'opacity-dot'},
               ),
        html.P("Название графика", style = P_STYLE),
        dcc.Input(id={'index':ind, 'type':"name-dot"}, type="text", placeholder="Название", style = INPUT_STYLE, persistence='local'),
        ]
    )]

def get_menu_pie(list_color_cols, ind):
    return [html.Div([
        html.P("Название секторов", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'xaxis'},
                     options=[x['options'] for x in list_color_cols], persistence='local'),
        html.P("Размер секторов", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'yaxis'},
                     options=[x['options'] for x in list_color_cols], persistence='local'),
        html.P("Количество уникальных секторов", style = P_STYLE),
        dcc.Slider(min=1, max=20, step=1, value=7, id={'index':ind, 'type':'sectors-slider'}, marks=None,
                    tooltip={"placement": "bottom", "always_visible": True}, persistence='local'),
        html.P("Агрегация", style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'agg-pie'},
                     options={
                         'sum': 'Сумма',
                         'avg': 'Среднее',
                         'count': 'Количество',
                         "countd":'Количество уникальных',
                         'min': 'Минимум',
                         'max': 'Максимум',
                         },
                     value='sum',
                     persistence='local'),
        html.P("Фильтр", style = P_STYLE),
        dbc.Row([

                dbc.Col([dcc.Dropdown(id={'index':ind, 'type':'filter-pie'},
                             options=[x['options'] for x in list_color_cols if x['type']=='object' or x['type']=='discrete'], persistence='local')], width = 5),
                dbc.Col([html.P(" входит в ")], width = 2),
                dbc.Col([dcc.Dropdown(id={'index':ind, 'type':'value_filter-pie'}, multi = True, persistence='local')], width = 5),
            ]),
        html.P("Название графика", style = P_STYLE),
        dcc.Input(id={'index':ind, 'type':"name-pie"}, type="text", placeholder="Название", style = INPUT_STYLE, persistence='local'),
        ]
    )]

def get_menu_table(list_color_cols, ind):
    return [html.Div( [
        html.Div(id = {'index':ind, 'type':'menu-columns-table'}, children = [
            html.P("Ось X", style = P_STYLE),
            dcc.Dropdown(id={'index':ind, 'type':'xaxis-table'},
                         options=[x['options'] for x in list_color_cols if x['type']=='object' or x['type']=='discrete'], persistence='local'),
            html.P("Ось Y", style = P_STYLE),
            dcc.Dropdown(id={'index':ind, 'type':'yaxis-table'},
                         options=[x['options'] for x in list_color_cols if x['type']=='object'or x['type']=='discrete'], multi=False, persistence='local'),
            html.P("Числовая метрика", style = P_STYLE),
            dcc.Dropdown(id={'index':ind, 'type':'zaxis-table'},
                         options=[x['options'] for x in list_color_cols if x['type']!='object'], multi=False, persistence='local'),
            html.P("Агрегация", style = P_STYLE),
            dcc.Dropdown(id={'index':ind, 'type':'agg-table'},
                         options={
                             'sum': 'Сумма',
                             'avg': 'Среднее',
                             'count': 'Количество',
                             "countd":'Количество уникальных',
                             'min': 'Минимум',
                             'max': 'Максимум',
                             },
                         value='sum',
                         persistence='local'),
            ],style = {'display':'none'}),
        dcc.Checklist(options = ['Корреляция'], value = ['Корреляция'], id = {'index':ind,'type':'correlation'}, persistence='local', style = P_STYLE),
        dcc.Dropdown(id={'index':ind, 'type':'correlation-type-table'},
                     options=[{'label':'Пирсон', 'value':'pearson'},
                              {'label':'Спирмен', 'value':'spearman'}], value = 'pearson', multi=False, persistence='local'),
        html.P("Фильтр", style = P_STYLE),
        dbc.Row([

                dbc.Col([dcc.Dropdown(id={'index':ind, 'type':'filter-table'},
                             options=[x['options'] for x in list_color_cols if x['type']=='object' or x['type']=='discrete'], persistence='local')], width = 5),
                dbc.Col([html.P(" входит в ")], width = 2),
                dbc.Col([dcc.Dropdown(id={'index':ind, 'type':'value_filter-table'}, multi = True, persistence='local')], width = 5),
            ]),
        html.P("Название графика", style = P_STYLE),
        dcc.Input(id={'index':ind, 'type':"name-table"}, type="text", placeholder="Название", style = INPUT_STYLE, persistence='local'),
        ]
    )]

def get_menu_text(current_index):
    # return [html.P("Название листа", style = P_STYLE),
    #         dcc.Input(id={'index':current_index, 'type':"name-text"}, type="text", placeholder="Название", style = INPUT_STYLE, persistence='local'),
    #         html.P("Текст", style = P_STYLE),
    #         dcc.Textarea(id={'index':current_index, 'type':'textarea-example'},
    #                      value='',
    #                      style={'width': '100%', 'height': 400, 'resize': 'none', 'align':'top'},
    #                      persistence='local'),
    #         html.P("Размер текста", style = P_STYLE),
    #         dcc.Slider(min=12, max=32, step=1, value=18, id={'index':current_index, 'type':'size-slider-text'}, marks=None,
    #                    tooltip={"placement": "bottom", "always_visible": True}, persistence='local')
    #         ]
    return [html.P("Название листа", style = P_STYLE),
            dcc.Input(id={'index':current_index, 'type':"name-text"}, type="text", placeholder="Название", style = INPUT_STYLE, persistence='local'),
            html.P("Текст", style = P_STYLE),
            dcc.Textarea(id={'index':current_index, 'type':'textarea-example'},
                         value='',
                         style={'width': '100%', 'height': 400, 'resize': 'none', 'align':'top'},
                         persistence='local'),
            html.P("Размер текста", style = P_STYLE),
            dcc.Slider(min=12, max=32, step=1, value=18, id={'index':current_index, 'type':'size-slider-text'}, marks=None,
                       tooltip={"placement": "bottom", "always_visible": True}, persistence='local'),
            # html.P('Цвет текста', style = P_STYLE),
            # dcc.Input(id = {'index':current_index, 'type':'input-color'}, type='color', value='#000000'),
            html.P('Загрузить изображение', style = P_STYLE),
            dcc.Upload(
                id={'index':current_index, 'type':'upload-image'},
                children=html.Div(['Перетащите или ', html.A('выберите изображение')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px 0px'
                },
                multiple=True
            ),
            html.Div(id={'index':current_index, 'type':'uploaded-images'}),
            html.P('Прикрепить файл', style = P_STYLE),
            dcc.Upload(
                id={'index':current_index, 'type':'upload-file-text'},
                children=html.Div(['Перетащите или ', html.A('выберите файл')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px 0px'
                },
                multiple=False
            ),
            
            
            html.Div(id={'index':current_index, 'type':'uploaded-files'})
            ]

@callback(Output({'index': MATCH, 'type':'menu'}, 'children'),
          Output({'index':MATCH, 'type':'sheet'},'style', allow_duplicate=True),
          Output({'index':MATCH, 'type':'sheet'},'selected_style', allow_duplicate=True),
          Input({'index': MATCH, 'type':'chart_type'}, 'value'),
          State({'index': MATCH, 'type':'chart_type'}, 'id'),
          State('df-table', 'data'),
          State('df-table', 'hidden_columns'),
          prevent_initial_call=True)
def generate_menu(chart_type, chart_id, data, hidden_columns):

    current_index = chart_id['index']
    # print('generation', chart_type, current_index)

    df = pd.read_json(json.dumps(data), orient='records')

    # print(hidden_columns)
    cols = ['NA'] if 'NA' in df.columns else []
    cols += hidden_columns if hidden_columns else []
    df = df.drop(columns = cols)

    type_cols = dict()
    for col in df.columns:
        if df[col].dtype == 'object':
            type_cols[col] = {'style': {'color':'Blue'}, 'type':'object'}
        elif df[col].dtype == 'int64' and len(df[col].unique())<30:
            type_cols[col] = {'style': {'color':'Orange'}, 'type':'discrete'}
        else:
            type_cols[col] = {'style': {'color':'Green'}, 'type':df[col].dtype}

    list_color_cols = [{'options':{'label':html.Span([i], style=type_cols[i]['style']), 'value': i},
                       'type': type_cols[i]['type']} for i in df.columns]

    if chart_type == 'bar':
        chart = get_menu_bar(list_color_cols, current_index)
    elif chart_type == 'line':
        chart = get_menu_line(list_color_cols, current_index)
    elif chart_type == 'dot':
        chart = get_menu_scatter(list_color_cols, current_index)
    elif chart_type == 'pie':
        chart = get_menu_pie(list_color_cols, current_index)
    elif chart_type == 'table':
        chart =  get_menu_table(list_color_cols, current_index)
    elif chart_type == 'wordcloud':
        chart = get_menu_wordcloud(list_color_cols, current_index)
    elif chart_type=='text':
        chart = get_menu_text(current_index)
    style = {**tab_style, **custom_style_tab, 'background-image':f"url('https://github.com/yupest/nto/blob/master/src/{chart_type}.png?raw=true')"}
    return chart, style, style           

######################################## processing the name dashboard ########################################

html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Grid with Draggable Boxes</title>
    <script src="https://cdn.plot.ly/plotly-3.1.0-rc.0.min.js" charset="utf-8"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            height: 100vh;
            overflow: auto;
        }
        h1 {
            text-align: center;
        }
        .container {
            position: relative;
            width: 100%;
            height: 100%;
        }

        .smart-box {
            position: absolute;
/*            background-color: rgba(0, 123, 255, 0.7);*/
            border: 2px solid #ссс;
            border-radius: 5px;
            color: white;
            padding: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            min-width: 150px;
            minHeight: 150px;
            cursor: move;
            user-select: none;
            minHeight:0;
            flex-grow:0;
            display:flex;
        }
        .plot-container {
            flex-grow:1;
            height:98% !important;
            width:98% !important;
            min-width:0;
            display:flex;
        }
        .resizer {
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: #fff;
            border: 2px solid #999;
            border-radius: 50%;
            right: -5px;
            bottom: -5px;
            cursor: se-resize;
        }
    </style>
</head>
<body>
    <h1>HEADER</h1>
    <div class="container" id="container">
'''
html_template_end = '''
    </div>

    <script>
    const container = document.getElementById('container');
    const boxes = document.querySelectorAll('.smart-box');
    const margin = 30;

    // Функция для оптимального расположения
    function arrangeBoxes() {
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        const boxCount = boxes.length;

        // Вычисляем оптимальную сетку (n×n)
        const n = Math.ceil(Math.sqrt(boxCount));
        const boxWidth = (containerWidth - (n + 1) * margin) / n;
        const boxHeight = (containerHeight - (n + 1) * margin) / n;

        boxes.forEach((box, index) => {
            const col = index % n;
            const row = Math.floor(index / n);

            box.style.width = `${boxWidth}px`;
            box.style.height = `${boxHeight}px`;
            box.style.left = `${col * (boxWidth + margin) + margin}px`;
            box.style.top = `${row * (boxHeight + margin) + margin}px`;
        });
    }
// Map для хранения связей между блоками и графиками
const plotInstances = new Map();

// Функция инициализации графика
function initPlot(containerId, figure) {
    const container = document.getElementById(containerId);
    if (!container) return;

    Plotly.newPlot(containerId, figure.data, figure.layout, figure.config)
        .then(() => {
            plotInstances.set(containerId, container);
            observeResize(container);
        });
}

// Наблюдатель за изменениями размеров
function observeResize(element) {
    const observer = new ResizeObserver(entries => {
        for (let entry of entries) {
            const containerId = entry.target.id;
            if (plotInstances.has(containerId)) {
                Plotly.Plots.resize(containerId);
            }
        }
    });

    observer.observe(element);
}

// Инициализация всех графиков после загрузки
document.addEventListener('DOMContentLoaded', () => {
    // Инициализация каждого графика
    document.querySelectorAll('.plot-container').forEach(container => {
        const figure = JSON.parse(container.dataset.figure);
        initPlot(container.id, figure);
    });

    // Инициализация перетаскивания
    setupDragAndResize();
});
// Функции для перетаскивания
            function setupDragAndResize() {
                boxes.forEach(box => {
                    const resizer = box.querySelector('.resizer');
                    let isDragging = false;
                    let isResizing = false;
                    let offsetX, offsetY;
                    let startX, startY, startWidth, startHeight;

                    // Перетаскивание
                    box.addEventListener('mousedown', function(e) {
                        if (e.target === resizer) return;

                        isDragging = true;
                        offsetX = e.clientX - box.getBoundingClientRect().left;
                        offsetY = e.clientY - box.getBoundingClientRect().top;

                        box.style.zIndex = 1000;
                        e.preventDefault();
                    });

                    // Изменение размера
                    resizer.addEventListener('mousedown', function(e) {
                        isResizing = true;
                        startX = e.clientX;
                        startY = e.clientY;
                        startWidth = parseInt(document.defaultView.getComputedStyle(box).width, 10);
                        startHeight = parseInt(document.defaultView.getComputedStyle(box).height, 10);

                        box.style.zIndex = 1000;
                        e.preventDefault();
                        e.stopPropagation();
                    });

                    // Общая функция перемещения
                    document.addEventListener('mousemove', function(e) {
                        if (isDragging) {
                            box.style.left = (e.clientX - offsetX) + 'px';
                            box.style.top = (e.clientY - offsetY) + 'px';
                        }

                        if (isResizing) {
                            const width = startWidth + (e.clientX - startX);
                            const height = startHeight + (e.clientY - startY);

                            if (width > 50) box.style.width = width + 'px';
                            if (height > 50) box.style.height = height + 'px';
                        }
                    });

                    // Завершение действий
                    document.addEventListener('mouseup', function() {
                        isDragging = false;
                        isResizing = false;
                        box.style.zIndex = '';
                    });
                });
            }

arrangeBoxes();
const resizeObserver = new ResizeObserver(entries => {
  entries.forEach(entry => {
    const plotId = entry.target.id;
    if (plotId && Plotly) {
      Plotly.Plots.resize(plotId);
    }
  });
});

// 2. Применение ко всем графикам
document.querySelectorAll('.plot-container').forEach(container => {
  resizeObserver.observe(container);
});

new ResizeObserver(() => Plotly.Plots.resize('graph'));
    </script>
</body>
</html>'''
def create_plot_block(figure_data, uid):
    container_id = f"plot-{uid}"

    # Настройки адаптивности
    figure_data.setdefault('config', {})
    figure_data['config']['responsive'] = True

    figure_data.setdefault('layout', {})
    figure_data['layout']['autosize'] = True
    figure_data['layout']['margin'] = {'l': 20, 'r': 20, 't': 20, 'b': 20}

    return f'''
    <div class="smart-box" style="left:100px;top:100px;width:300px;height:250px;">
        <div class="plot-container"
             id="{container_id}"
             data-figure='{str(json.dumps(figure_data)).replace("'", '&apos;')}'></div>
        <div class="resizer"></div>
    </div>
    '''

@callback(
    Output("download-html", "data"),
    Input("save-html", "n_clicks"),
    State("dashboard", "children"),
    State('input-name-dashboard', 'value'),
    prevent_initial_call=True
)
def save_html(n_clicks, container_children, h1):
    if not n_clicks:
        raise PreventUpdate

    figures = []
    
    for i, comp in enumerate(container_children[0]['props']['children']):
        # print(comp['props']['children'], end = '\n--------')
        if ('type' in comp['props']['children']) and comp['props']['children']['type'] == 'Graph':
            figure_data = comp['props']['children']['props']['figure']
            figures.append(create_plot_block(figure_data, i))
            
        print(type(comp['props']['children']))
        try:
            text_blocks = []
            for item in comp['props']['children']:
                if item['type'] == 'P':
                    text = item['props']['children']
                    text_blocks.append(text)
                elif item['type'] == 'Img':
                    img = item['props']['src']
                    block = f'''
                    <div class="smart-box" style="left:100px;top:100px;width:300px;height:250px;">
                        <img src = "{img}"></img>
                        <div class="resizer"></div>
                    </div>
                    '''
                    figures.append(block)
            block = f'''
            <div class="smart-box" style="left:100px;top:100px;width:300px;height:250px;">
                <p style = "color:black;">{'<br>'.join(text_blocks)}</p>
                <div class="resizer"></div>
            </div>
            '''
            figures.append(block)
        except:
            continue

    if h1 is None:
        h1 = ''
    # Создаем HTML-строку
    html_str = html_template.replace('HEADER', h1)+ '\n'.join(figures)+html_template_end

    return {
        "content": html_str,
        "filename": "dash_charts.html",
        "type": "text/html"
    }

# Обработчики для загрузки изображений и файлов
@callback(
    Output({'index':MATCH, 'type':'uploaded-files'}, 'children'),
    Input({'index':MATCH, 'type':'upload-file-text'}, 'contents'),
    State({'index':MATCH, 'type':'upload-file-text'}, 'filename'),
    prevent_initial_call=True
)
def handle_uploads_images(file_content, file_filename):
    ctx_triggered = ctx.triggered_id
    files = []
    
    if file_content and 'upload-file-text' in str(ctx_triggered):
        files.append(html.Div([
            html.P(f"Файл: {file_filename}"),
            html.A("Скачать файл", href=file_content, download=file_filename, 
                   style={'display': 'inline-block', 'padding': '5px 10px', 'background': '#007bff', 
                          'color': 'white', 'text-decoration': 'none', 'border-radius': '3px'})
        ]))
    
    return files

# Обработчики для загрузки изображений и файлов
@callback(
    Output({'index':MATCH, 'type':'uploaded-images'}, 'children'),
    Input({'index':MATCH, 'type':'upload-image'}, 'contents'),
    State({'index':MATCH, 'type':'upload-image'}, 'filename'),
    prevent_initial_call=True
)
def handle_uploads_files(images_content, images_filename):
    ctx_triggered = ctx.triggered_id
    files = []
    
    if images_content and 'upload-image' in str(ctx_triggered):
        for image_content, image_filename in zip(images_content, images_filename):
            files.append(html.Div([
                html.P(f"Изображение: {image_filename}"),
                html.Img(src=image_content, style={'max-width': '100%', 'max-height': '200px'})
            ]))
            
        # files.append(html.Div([
        #     html.P(f"Изображение: {image_filename}"),
        #     html.Img(src=image_content, style={'max-width': '100%', 'max-height': '200px'})
        # ]))
    
    return files

# КОЛБЭКИ ДЛЯ ВЫЧИСЛИТЕЛЬНОГО ЭССЕ

@callback(
    Output('essay-sortable-list', 'children', allow_duplicate=True),
    Output('essay-order', 'data',allow_duplicate=True),
    Input('storage', 'data'),
    Input('essay-order', 'data'),
    
    prevent_initial_call=True
)
def update_essay_list(stored_data, current_order):
    print(current_order)
    if not stored_data or 'sheets' not in stored_data:
        return [], []
    
    sheets = list(stored_data['sheets'].keys())
    
    # Если порядок не задан или изменилось количество листов, создаем новый порядок
    if not current_order or len(current_order) != len(sheets):
        current_order = sheets
    
    # Создаем перетаскиваемые элементы
    sortable_items = []
    for sheet_name in current_order:
        if sheet_name in sheets:
            sortable_items.append(
                html.Div([
                    html.Div([
                        html.Span("☰", style={'cursor': 'grab', 'marginRight': '10px', 'color': '#666'}),
                        html.Span(sheet_name, style={'flexGrow': 1}),
                        html.Span("📊", style={'marginLeft': '10px'})
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'padding': '10px',
                        'margin': '5px 0',
                        'border': '1px solid #ccc',
                        'borderRadius': '3px',
                        'backgroundColor': 'white',
                        'cursor': 'grab'
                    })
                ], id={'type': 'essay-item', 'index': sheet_name}, 
                   style={'userSelect': 'none'},
                   draggable='true', 
                   **{'data-drag': sheet_name}
                   )
            )
    
    return sortable_items, current_order

@callback(
    Output('essay-order', 'data', allow_duplicate=True),
    Input({'type': 'essay-item', 'index': ALL}, 'id'),
    State('essay-order', 'data'),
    prevent_initial_call=True
)
def update_essay_order(item_ids, current_order):
    if not item_ids:
        return no_update
    
    # Получаем новый порядок из ID элементов
    new_order = [item_id['index'] for item_id in item_ids]
    return new_order


@app.callback(
    Output('essay-order', 'data', allow_duplicate=True),
    Input('essay-sortable-list', 'n_clicks'),
    State('essay-sortable-list', 'children'),
    prevent_initial_call=True
)
def update_order_from_drag(n_clicks, children):
    if not children:
        return no_update
    
    # Извлекаем порядок из ID дочерних элементов
    new_order = []
    for child in children:
        if 'props' in child and 'id' in child['props']:
            sheet_name = child['props']['id']['index']
            new_order.append(sheet_name)
    
    return new_order


@callback(
    Output('essay-preview', 'children'),
    Input('essay-order', 'data'),
    Input('storage', 'data'),
    prevent_initial_call=True
)
def update_essay_preview(order, stored_data):
    if not order or not stored_data or 'sheets' not in stored_data:
        return html.P("Добавьте листы визуализации для создания эссе", 
                     style={'textAlign': 'center', 'color': '#666', 'marginTop': '50px'})
    
    essay_content = []
    
    for i, sheet_name in enumerate(order, 1):
        if sheet_name in stored_data['sheets']:
            sheet_data = stored_data['sheets'][sheet_name]
            
            # Добавляем заголовок листа
            essay_content.append(
                html.Div([
                    html.H3(f"{i}. {sheet_name}", 
                           style={'borderBottom': '2px solid #007bff', 
                                 'paddingBottom': '10px',
                                 'marginTop': '30px'})
                ], style={'marginBottom': '20px'})
            )
            
            # Добавляем содержимое листа (заглушка - в реальности нужно получить визуализацию)
            essay_content.append(
                html.Div([
                    html.P(f"Визуализация: {sheet_name}", 
                          style={'padding': '20px', 
                                'backgroundColor': '#f8f9fa',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'color': '#666'})
                ], style={'marginBottom': '30px'})
            )
    
    return essay_content

@callback(
    Output("download-essay", "data"),
    Input("save-essay", "n_clicks"),
    State("essay-order", "data"),
    State("storage", "data"),
    State('input-name-essay', 'value'),
    prevent_initial_call=True
)
def download_essay(n_clicks, order, stored_data, essay_title):
    if not n_clicks:
        raise PreventUpdate
    
    if not essay_title:
        essay_title = "Вычислительное эссе"
    
    if not order or not stored_data or 'sheets' not in stored_data:
        return {
            "content": f"<h1>{essay_title}</h1><p>Нет данных для отображения</p>",
            "filename": f"{essay_title}.html",
            "type": "text/html"
        }
    
    # Создаем HTML-структуру для эссе
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{essay_title}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .essay-container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .essay-title {{
                text-align: center;
                color: #333;
                margin-bottom: 40px;
                border-bottom: 3px solid #007bff;
                padding-bottom: 20px;
            }}
            .sheet-section {{
                margin-bottom: 50px;
                padding: 20px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #fff;
            }}
            .sheet-title {{
                color: #007bff;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .visualization {{
                text-align: center;
                margin: 20px 0;
            }}
            .chart-container {{
                width: 100%;
                height: 400px;
                margin: 20px 0;
            }}
            @media (max-width: 768px) {{
                .essay-container {{
                    padding: 20px;
                }}
                .sheet-section {{
                    padding: 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="essay-container">
            <h1 class="essay-title">{essay_title}</h1>
    """
    
    # Добавляем содержимое каждого листа в порядке эссе
    for i, sheet_name in enumerate(order, 1):
        if sheet_name in stored_data['sheets']:
            html_content += f"""
            <div class="sheet-section">
                <h2 class="sheet-title">{i}. {sheet_name}</h2>
                <div class="visualization">
                    <div id="chart-{uuid.uuid4()}" class="chart-container">
                        <!-- Здесь будет визуализация -->
                        <p>Визуализация: {sheet_name}</p>
                    </div>
                </div>
            </div>
            """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    return {
        "content": html_content,
        "filename": f"{essay_title}.html",
        "type": "text/html"
    }

# JavaScript для перетаскивания (добавляем в конец файла)
essay_drag_script = """
// Функция для обработки перетаскивания
function setupEssayDragAndDrop() {
    const container = document.getElementById('essay-sortable-list');
    let draggedItem = null;
    
    // Обработчики событий перетаскивания
    container.addEventListener('dragstart', function(e) {
        if (e.target.getAttribute('draggable') === 'true' || 
            e.target.parentElement.getAttribute('draggable') === 'true') {
            draggedItem = e.target.getAttribute('draggable') === 'true' ? e.target : e.target.parentElement;
            setTimeout(() => {
                draggedItem.style.opacity = '0.4';
            }, 0);
        }
    });
    
    container.addEventListener('dragend', function(e) {
        if (draggedItem) {
            draggedItem.style.opacity = '1';
            draggedItem = null;
        }
    });
    
    container.addEventListener('dragover', function(e) {
        e.preventDefault();
        const afterElement = getDragAfterElement(container, e.clientY);
        const draggable = draggedItem;
        if (afterElement == null) {
            container.appendChild(draggable);
        } else {
            container.insertBefore(draggable, afterElement);
        }
    });
    
    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('[draggable="true"]')];
        
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', setupEssayDragAndDrop);

"""

# Добавляем скрипт в layout
app.clientside_callback(
    f"""
    <script>
    {essay_drag_script}
    function() {{
        return setupEssayDragAndDrop();
    }}
    </script>
    """,
    Output('essay-sortable-list', 'children'),
    Input('essay-sortable-list', 'children')
)


# running the server
if __name__ == '__main__':
    app.run(debug=True, host = '127.0.0.1', port = 5001)
