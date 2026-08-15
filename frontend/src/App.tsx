/**
 * Casca da aplicação: marcos, navegação e roteamento.
 *
 * A estrutura de marcos (`banner`, `navigation`, `main`, `contentinfo`) não é
 * decoração semântica: é o mapa pelo qual o usuário de leitor de tela navega.
 * Junto com o link de salto, é o que permite ir direto ao conteúdo em vez de
 * ouvir o cabeçalho inteiro a cada troca de tela.
 */

import { NavLink, Route, Routes } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { DetalheDaVarredura } from './pages/DetalheDaVarredura';
import { Alvos } from './pages/Alvos';
import { Referencia } from './pages/Referencia';
import { NaoEncontrada } from './pages/NaoEncontrada';

const ROTAS = [
  { para: '/', rotulo: 'Painel', fim: true },
  { para: '/alvos', rotulo: 'Alvos auditados', fim: false },
  { para: '/referencia', rotulo: 'Matriz WCAG e LBI', fim: false },
] as const;

export function App() {
  return (
    <>
      {/* 2.4.1 — mecanismo de bypass dos blocos repetidos. */}
      <a className="pular-para-conteudo" href="#conteudo">
        Pular para o conteúdo principal
      </a>

      <header className="cabecalho-app">
        <div className="envoltorio cabecalho-app__conteudo">
          <a className="marca" href="/">
            AcessiSaúde-Audit
            <span>Auditoria de acessibilidade e direitos digitais em saúde pública</span>
          </a>

          {/* aria-label distingue esta navegação de outras que possam existir. */}
          <nav className="navegacao-principal" aria-label="Navegação principal">
            <ul>
              {ROTAS.map((rota) => (
                <li key={rota.para}>
                  {/* NavLink aplica aria-current="page" quando ativo — é isso
                      que o leitor de tela anuncia. O destaque visual em CSS é
                      apenas reforço, e é derivado do próprio atributo
                      (seletor [aria-current='page']), o que impede que os dois
                      sinais divirjam. */}
                  <NavLink to={rota.para} end={rota.fim}>
                    {rota.rotulo}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </header>

      <main id="conteudo" className="envoltorio">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/varreduras/:id" element={<DetalheDaVarredura />} />
          <Route path="/alvos" element={<Alvos />} />
          <Route path="/referencia" element={<Referencia />} />
          <Route path="*" element={<NaoEncontrada />} />
        </Routes>
      </main>

      <footer className="rodape-app">
        <div className="envoltorio">
          <p>
            Instrumento de auditoria técnica e de pesquisa acadêmica. Não
            constitui parecer jurídico nem prova pericial: as proposições
            jurídicas apresentadas indicam fundamentos normativos aplicáveis
            segundo a matriz documentada do projeto, e sua adequação ao caso
            concreto depende de análise profissional.
          </p>
        </div>
      </footer>
    </>
  );
}
