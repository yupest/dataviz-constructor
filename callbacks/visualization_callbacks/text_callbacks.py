from dash import html, Input, Output, State, dcc
from dash import ctx
from dash.dependencies import MATCH

def register_text_callbacks(app):

        
    # Обработчики для загрузки изображений и файлов
    @app.callback(
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

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
            Input({'index':MATCH, 'type':'textarea-example'}, 'value'),
            # Input({'index':MATCH, 'type':'size-slider-text'}, 'value'),
            Input({'index':MATCH, 'type':'iframe-code'}, 'value'), 
            Input({'index':MATCH, 'type':'upload-image'}, 'contents'), 
            Input({'index':MATCH, 'type':'sheet'}, 'value'),
            prevent_initial_call=True
        )
    def update_output(text, iframe_code, images_content, sheet):
        res = []
        # for p in text.splitlines():
        
        res.append(dcc.Markdown(text))
            
        res_imgs = []
        if images_content:
            for image_content in images_content:
                res_imgs.append(html.Img(src=image_content, style={'max-width': '100%', 'max-height': '100%', 'object-fit': 'contain'}))
            
        # iframe (если есть) — отобразим под текстом/изображениями
        # iframe_block = None
        if iframe_code:
            # iframe_code может быть либо прямым <iframe...> либо src url. Попробуем безопасно вставить <iframe>
            try:
                res.append(html.Iframe(srcDoc=iframe_code, style={'width':'100%', 'height':'400px', 'border':'none'}))
            except Exception:
                # fallback: если это URL
                res.append(html.Iframe(src=iframe_code, style={'width':'100%', 'height':'400px', 'border':'none'}))
        
        return [*res, *res_imgs]