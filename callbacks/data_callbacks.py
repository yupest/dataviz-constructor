from dash import Dash, Output, Input, State
import pandas as pd
import base64
import io

def parse_contents(contents, filename):
    df_uploaded = pd.DataFrame()

    if contents:
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            if 'csv' in filename:
                df_uploaded = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                df_uploaded = pd.read_excel(io.BytesIO(decoded))
            elif 'json' in filename:
                df_uploaded = pd.read_json(io.StringIO(decoded.decode('utf-8')))

        except Exception as e:
            print(f'parse content for {filename}', e)

    return df_uploaded

def register_data_callbacks(app):
    ######################################## processing the data ########################################
    @app.callback([Output('raw-data', 'data'),
           Output('storage', 'data', allow_duplicate=True)],
           Input('upload-data', 'contents'),  # Триггер
           State('upload-data', 'filename'),  # Дополнительные данные
           prevent_initial_call=True
    )
    def set_data(contents, filename):
        # print('--------------------set_data------------------')
        json_data = {
            'filename': filename,
            'data': '[]',
            'hidden_columns': []
        }
        if not contents:
            # print('contents')
            return json_data, None
            # raise PreventUpdate
        try:
            df = parse_contents(contents, filename)
            cols_exist = df.columns.to_list()
            # print(cols_exist)
            df['NA'] = (df.isna().any(axis=1) | (df == '').any(axis=1)).astype(int)
            df = df[['NA']+cols_exist]
            json_data['data'] = df.to_json(orient='records')
        except Exception as e:
            print(f"Error: {e}")
        # print('data: ', json_data['data'][:50])
        return json_data, None