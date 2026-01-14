from dash import Input, Output, State
from dash.exceptions import PreventUpdate
import json
import markdown as md

html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Grid with Draggable Boxes</title>
    <script src="https://cdn.plot.ly/plotly-3.1.0-rc.0.min.js" charset="utf-8"></script>
    <script src="https://cdn.jsdelivr.net/gh/timdream/wordcloud2.js@gh-pages/src/wordcloud2.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@highlightjs/cdn-assets@11.11.1/styles/default.min.css">
    <script src="https://unpkg.com/@highlightjs/cdn-assets@11.11.1/highlight.min.js"></script>
    <script>hljs.highlightAll();</script>
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
        .wordcloud-container {
            width: 100%;
            text-align: center;
            margin: 10px 0;
            object-fit: contain;
        }
        .wordcloud-canvas {
            background: white;
            height:100%;
            width:auto;
        }
        /* Стили для iframe */
        .iframe-content {
            width: 100%;
            height: 350px;
            min-height: 250px;
            background: white;
            margin: 10px 0;
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
        .markdown-content {
            color: black;
            width: 100%;
            height: 100%;
            overflow: auto;
            padding: 10px;
            box-sizing: border-box;
        }
        
        .markdown-content h1, 
        .markdown-content h2, 
        .markdown-content h3 {
            margin-top: 0;
            margin-bottom: 10px;
        }
        
        .markdown-content p {
            margin-bottom: 10px;
        }
        
        .markdown-content ul, 
        .markdown-content ol {
            margin-left: 20px;
            margin-bottom: 10px;
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
// Функция для инициализации Wordcloud
function initWordcloud(canvasId, wordcloudData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Преобразуем данные в формат для wordcloud2
    const words = wordcloudData.list.map(item => [item[0], item[1]]);
    
    WordCloud(canvas, {
        list: words,
        gridSize: wordcloudData.gridSize,
        weightFactor: wordcloudData.weightFactor,
        fontFamily: 'Arial, sans-serif',
        color: wordcloudData.color,
        backgroundColor: wordcloudData.backgroundColor,
        rotateRatio: wordcloudData.rotateRatio,
        ellipticity: wordcloudData.ellipticity,
        shuffle: wordcloudData.shuffle
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
    
    // Инициализация Wordcloud
    document.querySelectorAll('.wordcloud-canvas').forEach(canvas => {
        try {
            const wordcloudData = JSON.parse(canvas.dataset.wordcloud);
            initWordcloud(canvas.id, wordcloudData);
        } catch (error) {
            console.error('Error initializing wordcloud:', canvas.id, error);
        }
    });
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
    
def register_dashboard_callbacks(app):
    ######################################## processing the name dashboard ########################################

    @app.callback(
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
        
        # for i, comp in enumerate(container_children[0]['props']['children']):
        #     print(comp)
        #     print()
        #     # comp = component['props']['children']
        #     # print(comp['props']['children'], end = '\n--------')
        #     if ('type' in comp['props']['children']) and comp['props']['children']['type'] == 'Graph':
        #         figure_data = comp['props']['children']['props']['figure']
        #         figures.append(create_plot_block(figure_data, i))
                
        #     # print(type(comp['props']['children']))
        #     try:
        #         text_blocks = []
        #         for item in comp['props']['children']:
        #             if item['type'] == 'P':
        #                 text = item['props']['children']
        #                 text_blocks.append(text)
        #             elif item['type'] == 'Img':
        #                 img = item['props']['src']
        #                 block = f'''
        #                 <div class="smart-box" style="left:100px;top:100px;width:300px;height:250px;">
        #                     <img src = "{img}"></img>
        #                     <div class="resizer"></div>
        #                 </div>
        #                 '''
        #                 figures.append(block)
        #         block = f'''
        #         <div class="smart-box" style="left:100px;top:100px;width:300px;height:250px;">
        #             <p style = "color:black;">{'<br>'.join(text_blocks)}</p>
        #             <div class="resizer"></div>
        #         </div>
        #         '''
        #         figures.append(block)
        #     except:
        #         continue
            
        
        for i, content in enumerate(container_children[0]['props']['children'], 1):
            comp = content['props']['children']
            type_sheet = comp.get('type')
            if type_sheet == 'Graph':
                figure_data = comp['props']['figure']
                figures.append(create_plot_block(figure_data, i))
                
            elif type_sheet == 'Div':
                items = comp['props']['children']
            
                if isinstance(items, dict) and ('type' in items) and items['type'] == 'DashWordcloud':
                    wordcloud_data = items['props']
            
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
                    
                    figures.append(f'''
                    <div class="smart-box" style="left:100px;top:100px;width:300px;height:250px;">
                        <div class="wordcloud-container">
                            <canvas id="wordcloud-{i}" 
                                    width="{wordcloud_data['width']}" 
                                    height="{wordcloud_data['height']}"
                                    class="wordcloud-canvas"
                                    data-wordcloud="{wordcloud_json}">
                            </canvas>
                        </div>
                        <div class="resizer"></div>
                    </div>
                    ''')
                else: 
                    try:
                        text_blocks = []
                        for item in items:
                            # if item['type'] == 'P':
                                
                            #     text = item['props']['children']
                            #     text_style = '; '.join([f'{k}: {v}' for k,v in item['props']['style'].items()])
                            #     text_blocks.append(f'<p style = "color:black;{text_style}">{text}</p>')
                            if item['type'] == 'Markdown':
                                markdown_text = item['props']['children']
                                md_content = md.markdown(markdown_text, extensions = [
                                                'fenced_code',      # Блоки кода с ```
                                                'tables',           # Таблицы
                                                'toc',              # Оглавление
                                                'nl2br',            # Переносы строк
                                                'sane_lists'        # Умные списки
                                            ])
                                text_blocks.append(f'''
                                <div class="markdown-content">
                                    {md_content}
                                </div>
                                ''')
                            elif item['type'] == 'Img':
                                img = item['props']['src']
                                figures.append(f'''
                                <div class="smart-box" style="left:100px;top:100px;width:300px;height:250px;">
                                    <img class="image-content" src="{img}" alt="Изображение" style = "width: 100%;max-width: 100%;max-height: 100%;object-fit: contain;">
                                    <div class="resizer"></div>
                                </div>
                                ''')
                            elif item['type'] == 'Iframe':
                                type_src = 'srcDoc' if 'srcDoc' in item['props'] else 'src'
                                iframe_content = item['props'].get(type_src, '')
                                figures.append(f'''
                                <div class="smart-box" style="left:100px;top:100px;width:300px;height:250px;">
                                    <iframe class="iframe-content" 
                                            srcdoc='{iframe_content}'
                                            frameborder="0"
                                            allowfullscreen>
                                    </iframe>
                                    <div class="resizer"></div>
                                </div>
                                ''')
                        block = f'''
                        <div class="smart-box" style="left:100px;top:100px;width:300px;height:250px;">
                            <div>{''.join(text_blocks)}</div>
                            <div class="resizer"></div>
                        </div>
                        '''
                        figures.append(block)
                    except Exception as e:
                        print(f"Error processing content: {e}")
                        print(comp)
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

    