import { kebabCase } from 'lodash';

export default (createElement, view) => {
    const { model } = view;
    const inheritedAttributes = ['children', 'slot', 'v_model', 'style_', 'class_', 'attributes'];
    const exposedProps = model.keys().filter(key => !key.startsWith('_') && !['style', 'layout'].includes(key)
        && !inheritedAttributes.includes(key));

    return createElement({
        created() {
            exposedProps.forEach(prop => model.on(`change:${prop}`, () => this.$forceUpdate()));
        },
        render(h) {
            return h(model.getVueTag(), {
                attrs: exposedProps.reduce((attrs, prop) => ({
                    ...attrs,
                    [kebabCase(prop)]: model.get(prop),
                }), {}),
                on: exposedProps.reduce((on, prop) => ({
                    ...on,
                    [kebabCase(prop)](v) {
                        model.set(prop, v);
                        model.save_changes(model.callbacks(view));
                    },
                }), {}),
            });
        },
    });
};
