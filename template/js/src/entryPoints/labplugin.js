const base = require('@jupyter-widgets/base');
const index = require('../index');

module.exports = {
    id: 'jupyter-pL4C3h0ld3r',
    requires: [base.IJupyterWidgetRegistry],
    activate(app, widgets) {
        widgets.registerWidget({
            name: 'jupyter-pL4C3h0ld3r',
            version: index.version,
            exports: index,
        });
    },
    autoStart: true,
};
