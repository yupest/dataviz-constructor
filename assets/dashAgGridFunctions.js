var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

// Функция для множественного выбора
dagcomponentfuncs.multipleSheetsRowDragText = function (params) {
    return `${params.rowNodes.length} sheet(s) selected`;
}
dagcomponentfuncs.onRowDragEnd = function(params) {
    // Передаем данные о событии в Dash
    const eventData = {
        node: params.node ? params.node.data : null,
        overNode: params.overNode ? params.overNode.data : null,
        event: params.event ? params.event.type : null,
        type: params.type
    };
    return eventData;
}