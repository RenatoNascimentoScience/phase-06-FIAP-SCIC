# Contratos dos módulos complementares

As funcionalidades deste documento recebem dados, retornam resultados e não
realizam interação com o terminal. O menu permanece em `codigo_fonte.py` e será
integrado pelo integrante responsável pela interface. A leitura e as opções 1 a
4 existentes serão preservadas.

## Interfaces

| Módulo | Interface | Resultado |
| --- | --- | --- |
| `src.alertas` | `FilaAlertas(dados)` | Fila de registros em alerta ou manutenção. |
| `src.alertas` | `inserir(registro)` | `True` se inserido; `False` para status ativo. |
| `src.alertas` | `proximo()` / `retirar()` | Registro, critérios e justificativa; `None` quando vazia. |
| `src.alertas` | `listar()` / `copiar()` | Lista em ordem de atendimento / fila independente. |
| `src.busca` | `buscar_por_prefixo(dados, campo, prefixo)` | DataFrame independente, na ordem original. |
| `src.dispositivos` | `converter_bases(valor)` | Dicionário com `decimal`, `binario` e `hexadecimal`. |
| `src.dispositivos` | `analisar_dispositivos(dados)` | DataFrame com `potencia_w` e unidades em `attrs['unidades']`. |
| `src.analise` | `gerar_analise_final(dados)` | Dicionário com contagens, alertas, resumo elétrico, recomendações e limitações. |

## Condições de uso

- Importar os módulos com `from src...` a partir da raiz do projeto.
- Passar o DataFrame original carregado pela função existente; não é necessário
  executar o cálculo de indicadores antes das funcionalidades novas.
- Os módulos não modificam o DataFrame recebido. O menu deve tratar `ValueError`
  e apresentar sua mensagem ao usuário.
- Consultas de prefixo aceitam apenas os campos `modulo` e `codigo_sensor`.
- Em entradas vazias, preservar a estrutura das tabelas e retornar filas/listas
  vazias; agregações sem observações serão representadas por `None`.
- Prioridade e criticidade são inteiros não negativos; ciclo é inteiro positivo;
  `modulo_essencial` aceita 0 ou 1. Tensão, corrente e latências são números
  finitos não negativos. Não são limites físicos universais.
- O índice da trie utiliza posições das linhas, evitando confundir índices
  repetidos do Pandas com registros repetidos.
- A avaliação do modelo continuará na opção 4. A síntese nova não treina outro
  modelo, não captura texto do terminal e não atribui métricas ao modelo.

## Distribuição das branches

1. `chore/estrutura-modulos`: contratos, estrutura, dependências e preservação.
2. `feat/alertas-heap`, `feat/busca-trie`, `feat/bases-eletricidade`: funcionalidades
   independentes baseadas na estrutura comum.
3. `feat/analise-final`: depende de heap e eletricidade.
4. `feat/menu-terminal`: reservada ao integrante da interface.
5. `docs/entrega-scic`: documentação e preparação da entrega.

Cada branch será revisada em um pull request próprio. A integração na `main`
depende da revisão do grupo. Não refatorar as funções anteriores durante esse
processo.
