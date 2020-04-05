import { Provider } from 'react-redux';
import reducer from './reducers';
import { createLoguxCreator } from '@logux/redux';
import { badge, badgeEn, log } from '@logux/client';
import { badgeStyles } from '@logux/client/badge/styles';
import React from 'react';
import ReactDOM from 'react-dom';
import App from "./App";

const createStore = createLoguxCreator({
    subprotocol: '1.0.0',
    server: process.env.NODE_ENV === 'development'
        ? 'ws://localhost:31337'
        : 'wss://logux.example.com',
    userId: false,  // TODO: We will fill it in next chapter
    credentials: '' // TODO: We will fill it in next chapter
});
const store = createStore(reducer);
badge(store.client, { messages: badgeEn, styles: badgeStyles });
log(store.client);
store.client.start();

ReactDOM.render(
    <Provider store={store}><App/></Provider>,
    document.getElementById('root')
);