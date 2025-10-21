from dash import Input, Output, State, no_update, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import ALL, MATCH
import pandas as pd
from dash.exceptions import PreventUpdate
from .utils import *
import copy
import json

def register_tabs_callbacks(app):
    # При загрузке страницы читаем данные из хранилища
    @app.callback(
        Output("tabs", "children"),
        Output("tabs", "value"),
        Output("storage", "data", allow_duplicate=True),
        Output('dashboard-items', 'children'),
        Output('sheets-drag-grid', 'rowData'),
        Input("storage", "data"),
        prevent_initial_call='initial_duplicate'
    )
    def load_tabs(storage):
        if not storage:
            raise PreventUpdate()
            
        if not storage.get('sheets') or storage.get('sheets') == dict():
            # Удаление всех страниц — создаем лист по умолчанию
            tab = dcc.Tab(id = {'index':'sheet_1', 'type':'sheet'}, label = 'Лист 1', value = 'sheet_1', children = [

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

            storage['sheets'] = {'sheet_1': {'name':'Лист 1', 'tab_content':tab}}
            storage['active_tab'] = 'sheet_1'
            dashboard = html.Div(id={'index':"sheet_1", 'type':'dashboard'},
                     style={
                        "height":'100%',
                        "width":'100%',
                        "display":"flex",
                        "flex-direction":"column",
                        "flex-grow":"0"
                    })
            return [tab, append_sheet, drop_sheet], "sheet_1", storage, [dashboard], [{'name':'Лист 1', 'id':'sheet_1'}]
        else:
            # Восстанавливаем из хранилища
            tabs = [val['tab_content'] for key, val in storage["sheets"].items()]
            tabs.append(append_sheet)
            tabs.append(drop_sheet)

            dashboard = []
            
            sheets_name = storage.get('order_list', [{'name':v.get('name', 'Лист'), 'id':k} for k, v in storage['sheets'].items()])
            sheets_order = []
            for sheet_order in sheets_name:
                if sheet_order['id'] in storage['sheets']:
                    sheet_order['name'] = storage['sheets'][sheet_order['id']]['name']
                    sheets_order.append(sheet_order)
            for k, v in storage['sheets'].items():
                try:
                    item = copy.deepcopy(v['tab_content']["props"]['children'][1]["props"]['children'][0]["props"]['children'][1]['props']['children'][0]['props']['children'])
                    # print(item)
                    item['props']['id'] = None
                    if isinstance(item['props']['children'], dict):
                        if item['props']['children']['type'] == 'Graph':
                            figure_data = item['props']['children']['props']['figure']
                            item = dcc.Graph(
                                figure=figure_data,
                                responsive=True,
                                style={
                                    "minHeight": "0",
                                    "flexGrow": "1", 
                                    "height": "100%",
                                    "width": "100%"
                                },
                                config={'responsive': True}
                            ) 
                except Exception as e:
                    print(e)
                    item = []
                dashboard_item = html.Div(id={'index':k, 'type':'dashboard'}, 
                                          children = item,
                                          style={
                                            "height":'100%',
                                            "width":'100%',
                                            "display":"flex",
                                            "flex-direction":"column",
                                            "flex-grow":"0"
                                        })
                dashboard.append(dashboard_item)
                if {'name':v['name'], 'id':k} not in sheets_order:
                    sheets_order.append({'name':v['name'], 'id':k})
            
            return tabs, storage["active_tab"], no_update, dashboard, sheets_order

    @app.callback(
        Output("storage", "data", allow_duplicate=True),
        Output("confirm-delete", "displayed"),
        Output("confirm-delete", "message"),
        Input('tabs', 'value'),
        Input('tabs', 'children'),
        Input({'index': ALL, 'type':'menu'}, 'children'),
        Input({"index": ALL, "type": "sheet"}, 'label'),
        Input({'index': ALL, 'type':'top-slider-bar'}, 'value'),
        Input('tabs-menu','value'),
        State("storage", "data"),
        prevent_initial_call=True
    )
    def set_active_tab(active_tab, tabs, menu, label, top, tabs_menu, storage):
        if not storage:
            raise PreventUpdate
        if active_tab!='drop' and active_tab != 'add':
            storage['active_tab'] = active_tab
            # storage["sheets"] = {tab['props']['value']: tab for i, tab in enumerate(tabs[:-2])}
            for i, tab in enumerate(tabs[:-2]):
                storage["sheets"][tab['props']['value']]['tab_content'] = tab
                storage["sheets"][tab['props']['value']]['name'] = tab['props']['label']
        elif active_tab=='add':
            if len(storage['sheets'])<LIMIT_PAGE:
                number_tab = max([int(sheet.split('_')[-1]) for sheet in storage['sheets'].keys()])+1
                new_tab_name = f"Лист {number_tab}"
                new_key = f'sheet_{number_tab}'
                new_tab = dcc.Tab(label=new_tab_name, value=new_key, id = {'index':new_key, 'type':'sheet'}, children = [
                                dbc.Container([dcc.Dropdown( id= {'index':new_key, 'type' : 'chart_type'}, placeholder = 'Выберите тип диаграммы',
                                                            persistence='local', options=icons)],
                                              style = {'margin-top':10}, fluid=True),
                                dbc.Container([
                                    dbc.Row([
                                        dbc.Col([
                                            html.Div(id = {'index':new_key, 'type' : 'menu'})
                                        ], width={'size':4}),

                                        dbc.Col([
                                            dcc.Loading(html.Div(id = {'index':new_key, 'type' : 'chart'}, style = {'text-align':'center'}) , type="circle", style={"visibility":"visible", "filter": "blur(2px)", 'margin-top':'100px'})
                                        ], width={'size':8})

                                    ]),
                                ], fluid=True)
                    ], style = tab_style, selected_style=tab_style)
                storage["sheets"].update({new_key:{'tab_content':new_tab, 'name':new_tab_name}})
                # tabs = tabs[:-2] + [new_tab]
                # for tab in tabs[:-2]:
                #     storage["sheets"][f"sheet_{tab['props']['value'].split(' ')[-1]}"]['tab_content'] = tab
                # storage["sheets"][f'sheet_{number_tab}']['tab_content'] = new_tab
                # storage["sheets"][f'sheet_{number_tab}']['name'] = new_tab_name
                storage["active_tab"] = new_key

        else:
            return no_update, True, f'Вы уверены, что хотите удалить "{storage["active_tab"]}"?'
        print('names', [v['name'] for k, v in storage['sheets'].items()])
        return storage, no_update, no_update

    @app.callback(
        Output("storage", "data", allow_duplicate=True),
        Input("confirm-delete", "submit_n_clicks"),
        State('storage', 'data'),
        prevent_initial_call=True
    )
    def show_confirmation(n_clicks, storage):
        if not storage:
            raise PreventUpdate
        number_sheets = len(storage['sheets'])
        if n_clicks:
            if number_sheets == 1:
                storage['sheets'] = None
                # raise PreventUpdate
            else:
                active_tab = storage['active_tab']
                # idx_active_tab = f'sheet_{active_tab.split(" ")[-1]}'
                del storage["sheets"][active_tab]
                max_number_tab = max([int(sheet.split('_')[-1]) for sheet in storage['sheets'].keys()])
                # active_tab = f'Лист {max_number_tab}'
                storage['active_tab'] = f'sheet_{max_number_tab}'
            return storage
        return no_update
    
    @app.callback(
        Output('storage', 'data', allow_duplicate=True),
        Input('df-table', 'data'),
        State('storage', 'data'),
        prevent_initial_call=True
    )
    def save_table_edits(all_table_data, storage):
        """Обновляем данные в storage при любом редактировании таблицы"""
        if not storage or not storage.get("data"):
            raise PreventUpdate
        if not all_table_data or len(all_table_data) == 0 or all_table_data[0] is None:
            raise PreventUpdate

        try:
            df = pd.DataFrame(all_table_data)
            df["NA"] = (df.isna().any(axis=1) | (df == "").any(axis=1)).astype(int)
            storage["data"]['df'] = df.to_json(orient="records")
            print("✅ Изменения сохранены в storage")
        except Exception as e:
            print("Ошибка при сохранении таблицы:", e)
            raise PreventUpdate

        return storage
    
    @app.callback(Output({'index': MATCH, 'type':'menu'}, 'children'),
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