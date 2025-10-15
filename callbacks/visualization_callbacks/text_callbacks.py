from dash import html, Input, Output, State
from dash.dependencies import MATCH

# TODO: убрать стилевые константы в отдельный файл
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

def register_text_callbacks(app):
    @app.callback(Output({'index':MATCH, 'type':'sheet'},'label', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'style', allow_duplicate=True),
              Output({'index':MATCH, 'type':'sheet'},'selected_style', allow_duplicate=True),
              Input({'index':MATCH, 'type':'name-text'},'value'),
              State({'index':MATCH, 'type':'sheet'},'value'),
              prevent_initial_call=True)
    def rename_sheet_text(name, value):
        style = {**tab_style, **custom_style_tab, 'background-image':"url('https://github.com/yupest/nto/blob/master/src/text.png?raw=true')"}
        if not name:
            return value, style, style
        else:

            return name, style, style

    @app.callback(Output({'index':MATCH, 'type':'chart'}, 'children', allow_duplicate=True),
                  Output({'index':MATCH, 'type':'dashboard'}, 'children', allow_duplicate=True),
            Input({'index':MATCH, 'type':'textarea-example'}, 'value'),
            Input({'index':MATCH, 'type':'size-slider-text'}, 'value'),
            Input({'index':MATCH, 'type':'upload-image'}, 'contents'), prevent_initial_call=True
        )
    def update_output(text, size, images_content):
        res_text = []
        for p in text.splitlines():
            res_text.append(html.P(p,style = {'font-size': size}))

        res_imgs = []
        if images_content:
            for image_content in images_content:
                res_imgs.append(html.Img(src=image_content, style={'max-width': '100%', 'max-height': '100%', 'object-fit': 'contain'}))


        return [*res_text,*res_imgs], [*res_text,*res_imgs]