from dash import Input, Output, State, no_update, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import ALL, MATCH
import pandas as pd
from dash.exceptions import PreventUpdate
from .utils import *
import copy
import json
import base64
import io

def register_tabs_callbacks(app):
    
    @app.callback(Output('storage', 'data'),
              Input('upload-project', 'contents'),  # Триггер
              prevent_initial_call=True)
    def upload_project(contents):
        if not contents:
            raise PreventUpdate
            
        storage = ensure_app_state(None, True)
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            file_size_mb = len(decoded) / (1024 * 1024)
        
            if file_size_mb > 4.5:  # Близко к лимиту 5MB
                return no_update
            
            content = decoded.decode('utf-8')
            storage = json.loads(content)
        except Exception as e:
            raise PreventUpdate
        
        return storage
    
    
    @app.callback(Output('download-project', 'data'),
              Input('save-project', 'n_clicks'),
              State('storage', 'data'),
              prevent_initial_call=True)
    def download_project(download_btn, storage):
        return {
             "content": json.dumps(storage),
             "filename": f"project.json",
             "type": "json"
         }
    
        
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
            tab = create_vis_tab('Лист 1', 'sheet_1')

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

            sheets_name = storage.get(
                'order_list',
                [{'name': v.get('name', 'Лист'), 'id': k} for k, v in storage['sheets'].items()]
            )
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
                except Exception:
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
            for i, tab in enumerate(tabs[:-2]):
                storage["sheets"][tab['props']['value']]['tab_content'] = tab
                storage["sheets"][tab['props']['value']]['name'] = tab['props']['label']
        elif active_tab=='add':
            if len(storage['sheets'])<LIMIT_PAGE:
                number_tab = max([int(sheet.split('_')[-1]) for sheet in storage['sheets'].keys()])+1
                new_tab_name = f"Лист {number_tab}"
                new_key = f'sheet_{number_tab}'
                new_tab = create_vis_tab(new_tab_name, new_key)
                storage["sheets"].update({new_key:{'tab_content':new_tab, 'name':new_tab_name}})
                storage["active_tab"] = new_key

        else:
            return no_update, True, f'Вы уверены, что хотите удалить "{storage["active_tab"]}"?'
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
            else:
                active_tab = storage['active_tab']
                del storage["sheets"][active_tab]
                max_number_tab = max([int(sheet.split('_')[-1]) for sheet in storage['sheets'].keys()])
                storage['active_tab'] = f'sheet_{max_number_tab}'
            return storage
        return no_update
    

    @app.callback(Output({'index':MATCH, 'type':'sheet'},'label', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'style', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'selected_style', allow_duplicate=True),
              Input({'index':MATCH, 'type':'name-chart'},'value'),
              State({'index': MATCH, 'type':'chart_type'}, 'value'),
              prevent_initial_call=True)
    def rename_sheet(name, type_chart):
        style = {**tab_style, **custom_style_tab, 
                 '--tab-icon': f"url('/assets/src/{type_chart}.png')", 
                 '--tab-icon-size': '24px',
                 '--tab-label': f'"{name}"'}
        if not name:
            return no_update, style, style
        else:
            return name, style, style
    
    @app.callback(Output({'index': MATCH, 'type':'menu'}, 'children'),
              Output({'index':MATCH, 'type':'sheet'},'style', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'selected_style', allow_duplicate=True),
              Input({'index': MATCH, 'type':'chart_type'}, 'value'),
              State({'index': MATCH, 'type':'chart_type'}, 'id'),
              State('storage', 'data'),
              prevent_initial_call=True)
    def generate_menu(chart_type, chart_id, storage):

        current_index = chart_id['index']

        name = current_index
        try:
            name = storage['sheets'][current_index].get('name', current_index)
        except Exception:
            name = current_index

        data = storage['data']['df']
        hidden_columns = storage['data']['hidden_columns']
        
        df = pd.read_json(data, orient='records')

        cols = ['NA'] if 'NA' in df.columns else []
        cols += hidden_columns if hidden_columns else []
        df = df.drop(columns = cols)

        type_cols = dict()
        list_color_cols_default = [{'options':{'label':html.Span(['Названия метрик'], style={'color':'Blue'}), 'value': 'Названия метрик'}, 'type': 'object'},
                           {'options':{'label':html.Span(['Значения метрик'], style={'color':'Green'}), 'value': 'Значения метрик'},'type': 'float'}
                           ]
        list_color_cols = []
        for col in df.columns:
            if col in storage['data']['columns']['object']:
                type_cols = {'style': {'color':'Blue'}, 'type':'object'}
            elif col in storage['data']['columns']['discrete']:
                type_cols = {'style': {'color':'Orange'}, 'type':'discrete'}
            else:
                type_cols = {'style': {'color':'Green'}, 'type':df[col].dtype}
            list_color_cols.append({'options':{'label':html.Span([col], style=type_cols['style']), 'value': col},
                           'type': type_cols['type']})
        
        if chart_type not in ['wordcloud']:
            list_color_cols = list_color_cols_default+list_color_cols

        match chart_type:
            case 'bar': 
                chart = get_menu_bar(list_color_cols, current_index)
            case 'line':
                chart = get_menu_line(list_color_cols, current_index)
            case 'dot':
                chart = get_menu_scatter(list_color_cols, current_index)
            case 'pie':
                chart = get_menu_pie(list_color_cols, current_index)
            case 'table':
                chart =  get_menu_table(list_color_cols, current_index)
            case 'wordcloud':
                chart = get_menu_wordcloud(list_color_cols, current_index)
            case'text':
                chart = get_menu_text(current_index)
        # chart+= [html.Button('Обновить визуализацию', id =  {'index':current_index, 'type':'upd-chart'}, n_clicks=0, style=get_btn_style("up-loading"))]
        style = {**tab_style, **custom_style_tab, '--tab-icon': f"url('/assets/src/{chart_type}.png')", '--tab-icon-size': '24px'}
        return chart, style, style   