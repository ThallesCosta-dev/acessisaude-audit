/**
 * Página de endereço inexistente.
 *
 * Usa `role="alert"` e move o foco para o título: em uma aplicação de página
 * única, chegar a um endereço inválido não recarrega o documento, e sem esses
 * dois recursos o usuário de leitor de tela apenas ouviria silêncio.
 */

import { Link } from 'react-router-dom';
import { TituloDePagina } from '../components/ui';

export function NaoEncontrada() {
  return (
    <>
      <TituloDePagina>Endereço não encontrado</TituloDePagina>
      <div role="alert" className="aviso aviso--atencao">
        <p>
          O endereço solicitado não corresponde a nenhuma tela deste painel.
          Pode ter sido removido, ou o identificador da varredura pode estar
          incorreto.
        </p>
      </div>
      <p>
        <Link to="/">Voltar ao painel de auditorias</Link>
      </p>
    </>
  );
}
