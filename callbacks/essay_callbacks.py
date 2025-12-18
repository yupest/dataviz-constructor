from dash import html, Input, Output, State, no_update, ctx
from dash.exceptions import PreventUpdate
import copy
import json
import markdown as md

def register_essay_callbacks(app):
    # КОЛБЭКИ ДЛЯ ВЫЧИСЛИТЕЛЬНОГО ЭССЕ

    @app.callback(
        Output('storage', 'data', allow_duplicate=True),
        Output('essay-preview', 'children'),
        Input('update-essay', 'n_clicks'),
        State('sheets-drag-grid', 'virtualRowData'), # Текущий порядок данных в grid
        State('sheets-drag-grid', 'selectedRows'), # Текущий порядок данных в grid
        State('storage', 'data'),
        prevent_initial_call=True
    )
    def set_order_list(update_essay, order, selected_rows, storage):
        data_order = [i for i in order if i in selected_rows]
        if 'update-essay.n_clicks' == ctx.triggered[0]['prop_id'] and update_essay>0:
            storage['order_list'] = order
            
            essay_content = []
            
            for row in data_order:
                sheet_id = row['id']
                item = copy.deepcopy(storage['sheets'][sheet_id]['tab_content']["props"]['children'][1]["props"]['children'][0]["props"]['children'][1]['props']['children'][0]['props']['children'])
                item['props']['id']['type'] = 'essay'
                essay_content.append(
                    html.Div([item], style={'marginBottom': '30px'})
                )
            
            return storage, essay_content
        return no_update, no_update

    @app.callback(
        Output("download-essay", "data"),
        Input("save-essay", "n_clicks"),
        State('essay-preview', 'children'),
        State('input-name-essay', 'value'),
        prevent_initial_call=True
    )
    def download_essay(n_clicks, essay, essay_title):
        if not n_clicks:
            raise PreventUpdate
        
        if not essay_title:
            essay_title = "Вычислительное эссе"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{essay_title}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.plot.ly/plotly-3.1.0-rc.0.min.js" charset="utf-8"></script>
    <script src="https://cdn.jsdelivr.net/gh/timdream/wordcloud2.js@gh-pages/src/wordcloud2.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@highlightjs/cdn-assets@11.11.1/styles/default.min.css">
    <script src="https://unpkg.com/@highlightjs/cdn-assets@11.11.1/highlight.min.js"></script>
    <script>hljs.highlightAll();</script>
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
            margin-bottom: 20px;
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
        }}
        .sheet-section {{
            margin-bottom: 5px 30px;
            padding: 30px;
            // border: 1px solid #e0e0e0;
            // border-radius: 8px;
            background-color: #fff;
            // box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .sheet-title {{
            color: #007bff;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .visualization {{
            margin: 10px 0;
            width: 100%;
        }}
        .plot-container {{
            width: 100%;
            height: 500px;
            min-height: 400px;
            //padding: 10px;
            //background: #fafafa;
        }}
        /* Стили для текстовых блоков */
        .text-content {{
            width: 100%;
            line-height: 1.8;
            //font-size: 16px;
            // color: #333;
            margin: 10px 0 0 10px;
        }}
        /* Стили для изображений */
        .image-content {{
            width: 100%;
            max-width: 100%;
            height: auto;
            //border-radius: 6px;
            margin: 10px 0;
            //box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        /* Стили для iframe */
        .iframe-content {{
            width: 100%;
            height: 350px;
            min-height: 250px;
            background: white;
            margin: 10px 0;
        }}
        .wordcloud-container {{
            width: 100%;
            text-align: center;
            margin: 10px 0;
        }}
        .wordcloud-canvas {{
            background: white;
        }}
        
        .markdown-content {{
            color: black;
            width: 100%;
            height: 100%;
            overflow: auto;
            padding: 10px;
            box-sizing: border-box;
        }}
        
        .markdown-content h1, 
        .markdown-content h2, 
        .markdown-content h3 {{
            margin-top: 0;
            margin-bottom: 10px;
        }}
        
        .markdown-content p {{
            margin-bottom: 10px;
        }}
        
        .markdown-content ul, 
        .markdown-content ol {{
            margin-left: 20px;
            margin-bottom: 10px;
        }}
        
        @media (max-width: 768px) {{
            .wordcloud-canvas {{
                height: 400px;
            }}
            .essay-container {{
                padding: 20px;
            }}
            .sheet-section {{
                padding: 20px;
            }}
            .plot-container {{
                height: 400px;
                min-height: 300px;
            }}
            .iframe-content {{
                height: 400px;
                min-height: 300px;
            }}
            .text-content {{
                font-size: 14px;
            }}
        }}
        
        @media (max-width: 480px) {{
            body {{
                padding: 10px;
            }}
            .essay-container {{
                padding: 15px;
            }}
            .sheet-section {{
                padding: 15px;
                margin-bottom: 30px;
            }}
            .plot-container {{
                height: 350px;
                min-height: 250px;
            }}
            .iframe-content {{
                height: 350px;
                min-height: 250px;
            }}
        }}
    </style>
    <script>
        // Функция для инициализации Plotly графиков
    function initPlot(containerId, figure) {{
        const container = document.getElementById(containerId);
        if (!container) return;

        Plotly.newPlot(containerId, figure.data, figure.layout, {{
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        }});
    }}
    
    // Функция для инициализации Wordcloud
    function initWordcloud(canvasId, wordcloudData) {{
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        // Преобразуем данные в формат для wordcloud2
        const words = wordcloudData.list.map(item => [item[0], item[1]]);
        
        WordCloud(canvas, {{
            list: words,
            gridSize: wordcloudData.gridSize,
            weightFactor: wordcloudData.weightFactor,
            fontFamily: 'Arial, sans-serif',
            color: wordcloudData.color,
            backgroundColor: wordcloudData.backgroundColor,
            rotateRatio: wordcloudData.rotateRatio,
            ellipticity: wordcloudData.ellipticity,
            shuffle: wordcloudData.shuffle
        }});
    }}
    
    // Инициализация после загрузки DOM
    document.addEventListener('DOMContentLoaded', function() {{
        // Инициализация Plotly графиков
        document.querySelectorAll('.plot-container').forEach(container => {{
            try {{
                const figure = JSON.parse(container.dataset.figure);
                initPlot(container.id, figure);
            }} catch (error) {{
                console.error('Error initializing plot:', container.id, error);
            }}
        }});
        
        // Инициализация Wordcloud
        document.querySelectorAll('.wordcloud-canvas').forEach(canvas => {{
            try {{
                const wordcloudData = JSON.parse(canvas.dataset.wordcloud);
                initWordcloud(canvas.id, wordcloudData);
            }} catch (error) {{
                console.error('Error initializing wordcloud:', canvas.id, error);
            }}
        }});
    }});
    // Ресайз при изменении размера окна
    window.addEventListener('resize', resizePlots);
    
    </script>
</head>
<body>
    <div class="essay-container">
        <h1 class="essay-title">{essay_title}</h1>
        """

        for i, content in enumerate(essay, 1):
            comp = content['props']['children'][0]['props']['children']
            if ('type' in comp) and comp['type'] == 'Graph':
                figure_data = comp['props']['figure']
                container_id = f"plot-{i}"
                html_content += f'''
                <div class="sheet-section">
                        <div class="plot-container"
                             id="{container_id}"
                             data-figure='{str(json.dumps(figure_data)).replace("'", '&apos;')}'>
                        </div>
                </div>
                '''
            elif ('type' in comp) and comp['type'] == 'DashWordcloud':
                wordcloud_data = comp['props']
        
                # Экранируем JSON для data атрибута
                wordcloud_json = json.dumps({
                    'list': wordcloud_data['list'],
                    'gridSize': wordcloud_data['gridSize'],
                    'weightFactor': wordcloud_data['weightFactor'],
                    'color': wordcloud_data['color'],
                    'backgroundColor': wordcloud_data['backgroundColor'],
                    'rotateRatio': wordcloud_data['rotateRatio'],
                    'ellipticity': wordcloud_data['ellipticity'],
                    'shuffle': wordcloud_data['shuffle']
                }).replace('"', '&quot;')
                
                html_content += f'''
                <div class="sheet-section">
                    <div class="wordcloud-container">
                        <canvas id="wordcloud-{i}" 
                                width="{wordcloud_data['width']}" 
                                height="{wordcloud_data['height']}"
                                class="wordcloud-canvas"
                                data-wordcloud="{wordcloud_json}">
                        </canvas>
                    </div>
                </div>
                '''
            else: 
                try:
                    text_blocks = []
                    for item in comp:
                        if item['type'] == 'Markdown':
                            markdown_text = item['props']['children']
                            md_content = md.markdown(markdown_text, extensions = [
                                            'fenced_code',      # Блоки кода с ```
                                            'tables',           # Таблицы
                                            'toc',              # Оглавление
                                            'nl2br',            # Переносы строк
                                            'sane_lists'        # Умные списки
                                        ])
                            
                            text_style = ''
                            if 'style' in item['props']:
                                text_style = '; '.join([f'{k}: {v}' for k,v in item['props']['style'].items()])
                            
                            text_blocks.append(f'''
                            <div class="visualization" style = "{text_style}">
                                <div class="markdown-content">
                                    {md_content}
                                </div>
                            </div>
                            ''')
                        elif item['type'] == 'Img':
                            img = item['props']['src']
                            text_blocks.append(f'''
                            <div class="visualization">
                                <img class="image-content" src="{img}" alt="Изображение">
                            </div>
                            ''')
                        elif item['type'] == 'Iframe':
                            type_src = 'srcDoc' if 'srcDoc' in item['props'] else 'src'
                            iframe_content = item['props'].get(type_src, '')
                            text_blocks.append(f'''
                            <div class="visualization">
                                <iframe class="iframe-content" 
                                        srcdoc='{iframe_content}'
                                        frameborder="0"
                                        allowfullscreen>
                                </iframe>
                            </div>
                            ''')
                    html_content += f'''
                    <div class="sheet-section">
                        {''.join(text_blocks)}
                    </div>
                    '''
                except Exception as e:
                    continue
        
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
