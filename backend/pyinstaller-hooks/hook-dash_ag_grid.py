from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('dash_ag_grid', include_py_files=True)