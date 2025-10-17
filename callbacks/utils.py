def ensure_app_state(state):
    if not state:
        # 'data':{'filename':None, 'df':None, 'hidden_columns':[], 'filter_query':''}
        return {"data": None, "sheets": {}, "essay_order": [], "dashboard": {}}
    state.setdefault("sheets", {})
    state.setdefault("essay_order", [])
    state.setdefault("dashboard", {})
    return state