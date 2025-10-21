from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

import dash_draggable
import dash_ag_grid as dag


from callbacks.utils import *
from callbacks import register_all_callbacks



app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN, 'https://codepen.io/chriddyp/pen/bWLwgP.css' ], suppress_callback_exceptions=True)
server = app.server

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
    dcc.Tabs(id = 'tabs-menu', children = [dcc.Tab(label='Данные', children = [
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
                        dag.AgGrid(
                            id="sheets-drag-grid",
                            rowData=[],
                            getRowId="params.data.id",
                            columnDefs=columnDefs,
                            defaultColDef={
                                "filter": False,
                                "sortable": True,
                                "resizable": False,
                                "editable": False
                            },
                            columnSize="sizeToFit",
                            persistence = True,
                            persisted_props = ['selectedRows'],
                            dashGridOptions={
                                "rowDragManaged": True,
                                "rowDragMultiRow": False,
                                "rowSelection": {'mode': 'multiRow'},
                                "rowDragText": {"function": "sheetRowDragText(params)"},
                                "animateRows": True,
                                "suppressMoveWhenRowDragging": True,
                            },
                            style={"height": "600px", "width": "100%"}
                        ), 
                        html.Button(id = 'update-essay',children = ['Применить изменения'], style = BTN_style)
                    ], style={
                        'border': '1px solid #ddd',
                        'borderRadius': '5px',
                        'padding': '10px',
                        'height': 'calc(100vh - 200px)',  # Высота окна минус отступы
                        'minHeight': '300px',
                        'backgroundColor': '#f9f9f9',
                        'overflowY': 'auto',  # Скролл внутри левой панели если нужно
                        'display': 'flex',
                        'flexDirection': 'column'
                    }),
                    html.P("Перетащите листы для изменения порядка", 
                          style={'text-align': 'center', 'color': '#666', 'fontSize': '12px', 'marginTop': '10px'})
                ], width=3, style={
                    'height': '100vh',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'position': 'sticky',
                    'top': 0
                }),
                
                # Правая панель - предпросмотр эссе
                dbc.Col([
                    html.H4("Предпросмотр эссе", style={'text-align': 'center', 'margin-bottom': '20px'}),
                    html.Div(id='essay-preview', style={
                        'border': '1px solid #ddd',
                        'borderRadius': '5px',
                        'padding': '20px',
                        'height': 'calc(100vh - 200px)',  # Такая же высота как у левой панели
                        'minHeight': '600px',
                        'backgroundColor': 'white',
                        'overflowY': 'auto',  # Независимый скролл
                        'display': 'flex',
                        'flexDirection': 'column'
                    })
                ], width=9, style={
                    'height': '100vh',
                    'display': 'flex',
                    'flexDirection': 'column'
                })
            ], style={
                'height': '100vh',
                'margin': 0,
                'padding': '20px',
                'overflow': 'hidden'  # Отключаем скролл у всего Row
            }),
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

# running the server
if __name__ == '__main__':
    app.run(debug = False)
