from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_daq as daq

# TODO: убрать константы в отдельный файл

LIMIT_PAGE = 20

type_diagrams = {'bar':'Столбчатая', 'line':'Линейная', 'dot':"Точечная", 'table':'Цветная таблица', 'pie':"Круговая", 'text':"Текст", 'wordcloud':"Облако слов"}

icons = [{'label': html.Span([
                    html.Img(src=f"https://github.com/yupest/nto/blob/master/src/{k}.png?raw=true", height=25),
                    html.Span(v, style={ 'padding-left': 10})],
                   style={'align-items': 'center', 'justify-content': 'center'}),
          'value': k}  for k, v in type_diagrams.items()]

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
columnDefs = [
    
    {
        'field': 'name',
        'headerName': 'Название листа', 
        'rowDrag': True,
        "rowDragText": {"function": "multipleSheetsRowDragText(params)"},
        'checkboxSelection': False,
        'headerCheckboxSelection': True,
    },
    
]
drop_sheet = dcc.Tab(id = {'index':'drop', 'type':'sheet'}, label = '❌', value = 'drop', style = tab_style, selected_style=tab_style)
append_sheet = dcc.Tab(id = {'index':'add', 'type':'sheet'}, label = '➕', value = 'add', style = tab_style, selected_style=tab_style)


def get_btn_style(url):
    d = BTN_style.copy()
    d['backgroundImage'] = d['backgroundImage'].format(btn = url)
    return d

style_btn_dashboard = get_btn_style('download')
style_btn_dashboard['width'] = '100%'

# Или модифицируем существующую функцию:
def ensure_app_state(state, reset=False):
    """Обеспечивает корректный state, с опцией сброса"""
    if not state or reset:
        # Полный сброс
        return {"data": None, "sheets": {}, "essay_order": [], "dashboard": {}}
    
    # Дозаполнение (старое поведение)
    state.setdefault("sheets", {})
    state.setdefault("essay_order", [])
    state.setdefault("dashboard", {})
    return state

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
            html.P('Iframe code (HTML) / URL', style=P_STYLE),
            dcc.Textarea(id={'index':current_index, 'type':'iframe-code'}, placeholder='Вставьте HTML iframe или URL...', style={'width':'100%', 'height':'120px'}, persistence='local'),
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
            # html.P('Прикрепить файл', style = P_STYLE),
            # dcc.Upload(
            #     id={'index':current_index, 'type':'upload-file-text'},
            #     children=html.Div(['Перетащите или ', html.A('выберите файл')]),
            #     style={
            #         'width': '100%',
            #         'height': '60px',
            #         'lineHeight': '60px',
            #         'borderWidth': '1px',
            #         'borderStyle': 'dashed',
            #         'borderRadius': '5px',
            #         'textAlign': 'center',
            #         'margin': '10px 0px'
            #     },
            #     multiple=False
            # ),
            
            
            # html.Div(id={'index':current_index, 'type':'uploaded-files'})

            ]
