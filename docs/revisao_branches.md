# Branches e revisão das contribuições

As sete branches do plano foram criadas e publicadas. As seis contribuições
com alterações possuem pull requests em rascunho. A `main` permanece na versão
anterior; a integração depende da revisão do grupo.

| Ordem | Branch | Revisão |
| --- | --- | --- |
| 1 | `chore/estrutura-modulos` | [PR 2 — estrutura](https://github.com/RenatoNascimentoScience/phase-06-FIAP-SCIC/pull/2) |
| 2 | `feat/alertas-heap` | [PR 3 — heap](https://github.com/RenatoNascimentoScience/phase-06-FIAP-SCIC/pull/3) |
| 2 | `feat/busca-trie` | [PR 4 — trie](https://github.com/RenatoNascimentoScience/phase-06-FIAP-SCIC/pull/4) |
| 2 | `feat/bases-eletricidade` | [PR 5 — bases e eletricidade](https://github.com/RenatoNascimentoScience/phase-06-FIAP-SCIC/pull/5) |
| 3 | `feat/analise-final` | [PR 6 — análise](https://github.com/RenatoNascimentoScience/phase-06-FIAP-SCIC/pull/6) |
| 4 | `docs/entrega-scic` | [PR 7 — documentação e pacote](https://github.com/RenatoNascimentoScience/phase-06-FIAP-SCIC/pull/7) |
| Outro integrante | `feat/menu-terminal` | Reservada na estrutura comum; ainda sem alterações ou pull request. |

## Dependências

Os PRs de heap, trie, eletricidade e análise apontam inicialmente para
`chore/estrutura-modulos`. O PR de documentação aponta para `feat/analise-final`.
A análise incorpora heap e eletricidade; a documentação reúne também a trie.
Esses merges locais preservam os commits e permitem executar a versão completa
para revisão, sem alterar a `main`.

Revisar estrutura primeiro, depois as três funcionalidades independentes,
análise e documentação. Após integrar cada dependência na `main`, atualizar a
base dos PRs seguintes para `main`. Assim, as diferenças passam a mostrar apenas
o trabalho ainda não integrado. Manter merges que preservem os commits.

## Menu e entrega

O integrante do menu deverá incorporar as funcionalidades aprovadas à sua branch,
seguir `integracao_menu.md` e abrir seu próprio pull request. Os módulos podem
ser conferidos na branch `docs/entrega-scic` antes da integração.

O ZIP atual é candidato. Menu, atualização dos documentos para o estado integrado,
vídeo Não listado e link real permanecem com o grupo. Os pull requests não
representam submissão acadêmica ou entrega final.
