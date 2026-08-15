/**
 * Ponto de entrada da aplicação.
 *
 * `ScrollRestoration` do react-router não é usado: a rolagem é reposta pelo
 * próprio `TituloDePagina`, que move o foco ao topo do conteúdo. Repor a
 * rolagem sem mover o foco produziria a incoerência de o usuário de teclado
 * continuar navegando a partir do fim da página anterior.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { App } from './App';
import './styles/global.css';

const raiz = document.getElementById('root');
if (!raiz) {
  throw new Error('Elemento #root não encontrado no documento.');
}

createRoot(raiz).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);
