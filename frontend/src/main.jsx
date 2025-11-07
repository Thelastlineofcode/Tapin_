import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { ToastProvider } from './components/Toast';
import './styles.css';

const container = document.querySelector('#root');
const root = createRoot(container);
root.render(
  <ToastProvider>
    <App />
  </ToastProvider>
);
