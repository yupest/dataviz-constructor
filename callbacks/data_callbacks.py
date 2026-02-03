from dash import dcc, html, Output, Input, State, dash_table, no_update, ctx
import pandas as pd
import json
import base64
import io
from dash.exceptions import PreventUpdate
from .utils import *

def parse_contents(contents, filename):
    df_uploaded = pd.DataFrame()

    if contents:
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            if 'csv' in filename or 'txt' in filename:
                df_uploaded = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                df_uploaded = pd.read_excel(io.BytesIO(decoded))
            elif 'json' in filename:
                df_uploaded = pd.read_json(io.StringIO(decoded.decode('utf-8')))

        except Exception as e:
            pass

    return df_uploaded

# ========== Отдельная функция для сборки вёрстки ==========
def build_data_view(df, filename, object_list, discrete_list, num_list, hidden_columns = [], filter_query = ''):
    """Создает меню, таблицу данных и таблицу статистики"""
    # --- меню ---
    menu = html.Div([
        html.H3(filename, style={'textAlign': 'center', 'marginTop': 15}),
        html.Div([
            html.Button("Данные", id="show-data-btn", style=get_btn_style("datatable")),
            html.Button("Статистика", id="show-describe-btn", style=get_btn_style("describe")),
            dcc.Input(id="input-filename", type="text", placeholder="Название файла", style={
                'margin': '10px 0px 11.5px 2px', 'height': '38px',
                'border': '1px solid #ccc', 'borderRadius': '4px',
                'fontSize': '14px', 'verticalAlign': 'middle'
            }),
            html.Button("Энкодер", id="encoder-btn", style=get_btn_style("encode")),
            html.Button("Скачать", id="download-data-btn", style=get_btn_style("download")),
        ], style = {'text-align':'right', 'position': 'absolute','width': '75%','z-index': '1','margin-left': '25%'})
    ])
    
    styles = [{
            'if': {'column_id': 'NA'},
            'backgroundColor': '#FFE4B5'
            }]
    data_table = dash_table.DataTable(
                    id='df-table',
                    data=json.loads(df.to_json(orient='records')),
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
                    hidden_columns = hidden_columns,
                    filter_action="native",
                    filter_query=filter_query,
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
                    # persistence_type = 'memory',
                    # persisted_props = ['page_current', 'selected_columns', 'selected_rows'],
                    style_header = {
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
    # --- таблицы статистики ---
    # object_list = []
    # discrete_list = []
    # num_list = []
    # for col in df.columns:
    #     if df[col].dtype == 'object':
    #         object_list.append(col)
    #     elif df[col].dtype == 'int64' and len(df[col].unique())<30:
    #         discrete_list.append(col)
    #     else:
    #         num_list.append(col)

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

    print('object_list', object_list)

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

    df_copy = df.copy()
    df_copy[discrete_list] = df_copy[discrete_list].astype('object')

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
    describe_block = html.Div(
        id="show-describe",
        children=[html.P('Числовые переменные', style = {'fontWeight':'bold',  'font-size':'12pt', 'margin-top':'10px'}),
                   df_describe,
                   html.P('Категориальные переменные', style = {'fontWeight':'bold',  'font-size':'12pt', 'margin-top':'10px'}),
                   df_describe_object,
                   html.P('Обозначения', style = {'fontWeight':'bold',  'font-size':'12pt', 'margin-top':'10px'})]+variables,
        hidden=True,
        style={'marginTop': '58px'}
    )

    return html.Div([
        menu,
        html.Div(id="show-data", children=data_table, hidden=False),
        describe_block
    ])


def register_data_callbacks(app):
    ######################################## processing the data ########################################
    @app.callback(
           Output('storage', 'data', allow_duplicate=True),
           Output('output-datatable', 'children', allow_duplicate=True),
           Input('upload-data', 'contents'),  # Триггер
           State('upload-data', 'filename'),  # Дополнительные данные
           State('storage', 'data'),
           prevent_initial_call='initial_duplicate'
    )
    def upload_data(contents, filename, storage):
        if not contents:
            raise PreventUpdate
        try:
            df = parse_contents(contents, filename)
            if df.empty:
                return no_update, html.P("❌ Не удалось прочитать файл. Поддерживаемые форматы: CSV, XLSX, JSON.")

            cols_exist = df.columns.to_list()

            object_list = []
            discrete_list = []
            num_list = []
            for col, data_type in df.dtypes.items():
                if data_type == 'object':
                    object_list.append(col)
                elif data_type == 'int64' and len(df[col].unique())<30:
                    discrete_list.append(col)
                else:
                    num_list.append(col)

            df['NA'] = (df.isna().any(axis=1) | (df == '').any(axis=1)).astype(int)
            df = df[['NA']+cols_exist]

            storage = ensure_app_state(storage, True)
            storage['data'] = {
                'filename': filename,
                'df': df.to_json(orient='records'),
                'hidden_columns': [],
                'filter_query': '',
                'columns':{'object':object_list, 'discrete':discrete_list, 'numeric':num_list}
            }
        except Exception as e:
            print(e)
            raise PreventUpdate
        return storage, build_data_view(df, filename, object_list, discrete_list, num_list)
    
    ######################################## processing the data table ########################################
    @app.callback(Output('output-datatable', 'children', allow_duplicate=True),
                  Input('storage', 'data'),
                  prevent_initial_call=True)
    def restore_table(storage: dict):
        if not storage or not storage.get('data') or storage['data'].get('df') in [None, '[]']:
            return html.P('Загрузите файл данных')
        filename = storage['data']['filename']
        df = pd.read_json(io.StringIO(storage['data']['df']), orient='records')
        hidden_columns = storage['data']['hidden_columns']
        filter_query = storage['data']['filter_query']
        columns = storage['data']['columns']
        return build_data_view(df, filename, columns['object'], columns['discrete'], columns['numeric'], hidden_columns, filter_query = storage['data']['filter_query'])

    @app.callback(Output('show-data', 'hidden', allow_duplicate=True),
                  Output('show-describe', 'hidden', allow_duplicate=True),
                  Input('show-describe-btn', 'n_clicks'),
                  Input('show-data-btn', 'n_clicks'),
                  prevent_initial_call=True)
    def toggle_views(show_describe, show_data):
        if 'show-describe-btn' == ctx.triggered_id:
            return True, False
        else:
            return False, True
        
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
            return dcc.send_data_frame(df.to_csv, name+new+'csv', index = False)
        else:
            return no_update
    
    @app.callback(
        Output('storage', 'data', allow_duplicate=True),
        Input('df-table', 'data'),
        Input('df-table', 'hidden_columns'),
        State('storage', 'data'),
        prevent_initial_call=True
    )
    def save_table_edits(all_table_data, hidden_columns, storage):
        """Обновляем данные в storage при любом редактировании таблицы"""
        if not storage or not storage.get("data"):
            raise PreventUpdate
        if not all_table_data or len(all_table_data) == 0 or all_table_data[0] is None:
            raise PreventUpdate
    
        try:
            df = pd.DataFrame(all_table_data)
            df["NA"] = (df.isna().any(axis=1) | (df == "").any(axis=1)).astype(int)
            storage["data"]['df'] = df.to_json(orient="records")
            storage['data']['hidden_columns'] = hidden_columns
        except Exception as e:
            raise PreventUpdate
    
        return storage
        
        

    