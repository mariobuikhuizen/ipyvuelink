import { DOMWidgetView } from '@jupyter-widgets/base';
import Vue from 'vue'; // eslint-disable-line import/no-extraneous-dependencies
import BootstrapVue from 'bootstrap-vue';
import './styles.less';
import createLinkedComponent from '../link';

Vue.use(BootstrapVue);

export class BootstrapvueView extends DOMWidgetView {
    remove() {
        this.vueApp.$destroy();
        return super.remove();
    }

    render() {
        super.render();
        this.displayed.then(() => {
            const vueEl = document.createElement('div');
            this.el.appendChild(vueEl);

            const view = this;

            this.vueApp = new Vue({
                el: vueEl,

                render: (createElement) => {
                    // TODO: Don't use v-app in embedded mode
                    /* Prevent re-rendering of toplevel component. This happens on button-click in
                     * v-menu */
                    if (!this.ipyvuetifyApp) {
                        this.ipyvuetifyApp = createElement('div', { class: 'bootstrap-styles' }, [createLinkedComponent(createElement, view)]);
                    }

                    return this.ipyvuetifyApp;
                },
            });
        });
    }
}
