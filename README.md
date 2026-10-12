# SCIC — Sistema de Comunicação Interplanetária da Colônia

Protótipo acadêmico da Aurora Siger para organizar registros simulados, analisar
latências, avaliar uma previsão simples, priorizar alertas e consultar registros.
O escopo está descrito em [scic-instructions.md](scic-instructions.md).

## Estado da implementação

O código principal e o CSV do desenvolvimento anterior estão preservados.
As opções 1 a 4 do menu continuam disponíveis. Heap, trie, conversões, análise
elétrica e síntese operacional estão implementadas em módulos separados e
podem ser demonstradas pelo script de exemplos.

**A integração das opções 5 a 8 do menu é responsabilidade de outro integrante
e está pendente.** A gravação/publicação do vídeo também está pendente. O pacote
gerado nesta etapa é candidato para revisão, não a entrega final.

## Arquivos

| Arquivo ou pasta | Conteúdo |
| --- | --- |
| `codigo_fonte.py` | Menu e funcionalidades anteriores, sem alterações nesta etapa. |
| `dados_aurora_siger.csv` | 48 registros, seis módulos, 12 sensores e oito ciclos simulados. |
| `src/` | Heap, trie, bases numéricas, eletricidade e análise final sem interação de terminal. |
| `tests/` | Testes funcionais e verificação de preservação. |
| `docs/` | Contratos, guia de integração, evidências e roteiro do vídeo. |
| `scripts/` | Demonstração independente e preparação do ZIP. |
| `relatorio_tecnico.md` | Explicação técnica, resultados, impactos e limitações. |
| `requirements.txt` | Versões verificadas de NumPy, Pandas e scikit-learn. |
| `link_video.txt` | Pendência explícita; substituir pelo link real após a publicação. |

## Instalação e execução

Ambiente de referência: Python 3.12.10. No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe codigo_fonte.py
```

Não é necessário ativar o ambiente. Em outros sistemas, o executável do ambiente
fica em `.venv/bin/python`. As bibliotecas externas utilizadas são NumPy 2.5.0,
Pandas 2.3.3 e scikit-learn 1.9.0. `heapq`, `unittest`, `unicodedata`, `argparse`
e as demais ferramentas auxiliares pertencem à biblioteca padrão do Python.

Para demonstrar as funcionalidades novas e executar os testes:

```powershell
.\.venv\Scripts\python.exe -B scripts/demonstrar_modulos.py
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

O exemplo retorna dez alertas/manutenções na heap, COM-01 como primeiro atendimento,
oito registros para `com`, oito para `MED`, conversão do ciclo 7 e potência de
50,40 W no primeiro registro. Não substitui a integração do menu.

Para atualizar as evidências após uma execução:

```powershell
.\.venv\Scripts\python.exe -B scripts/demonstrar_modulos.py --saida docs/evidencias_modulos.json
```

Os scripts resolvem o CSV a partir da pasta do projeto e podem ser chamados
por caminho absoluto a partir de outro diretório.

## Integração e branches

Consultar [contratos dos módulos](docs/contratos_modulos.md) e
[guia para o integrante do menu](docs/integracao_menu.md).

Branches previstas: `chore/estrutura-modulos`, `feat/alertas-heap`,
`feat/busca-trie`, `feat/bases-eletricidade`, `feat/analise-final`,
`feat/menu-terminal` e `docs/entrega-scic`. Cada contribuição terá revisão
própria antes da integração na `main`.

## Relatório e apresentação

Ler [relatorio_tecnico.md](relatorio_tecnico.md) para fórmulas, critérios de
prioridade, interpretação do modelo e reflexão social, cultural e sustentável.
O [roteiro do vídeo](docs/roteiro_video.md) organiza uma apresentação inferior
a cinco minutos; gravar somente depois de concluir e verificar o menu.

## Preparação do pacote

```powershell
.\.venv\Scripts\python.exe -B scripts/preparar_entrega.py --candidato
```

Esse comando gera `output/scic-candidato-modulos.zip`, com as pendências
identificadas dentro do pacote. Após integração, publicação do vídeo e atualização
do relatório/README para o estado final, executar sem `--candidato`:

```powershell
.\.venv\Scripts\python.exe -B scripts/preparar_entrega.py
```

O empacotador recusa o pacote final enquanto houver chamadas provisórias no
código ou faltar um link com formato válido. Ele não verifica acesso ao YouTube,
duração do vídeo ou configuração Não listado; essas verificações cabem ao grupo.
Extrair o ZIP em outra pasta, instalar as dependências e repetir os testes antes
da submissão. Histórico Git, ambientes, caches e temporários não entram no ZIP.

## Limitações conhecidas

- Os dados são simulados; milissegundos representam latências operacionais da
  colônia, não o tempo físico de propagação entre planetas.
- As funções anteriores permanecem intactas: a consulta por módulo interpreta
  expressões regulares; o status com acento pode não coincidir com o CSV; erro
  relativo com observação zero não tem tratamento específico. A base fornecida
  não contém observações zero. As correções ficam para uma etapa posterior.
- Prioridades e ciclos são critérios simulados. A ordem do CSV desempata registros;
  não comprova uma ordem real de chegada.
- A regressão foi avaliada em uma divisão pequena; não há validação temporal de
  ciclos futuros. A síntese não recalcula o modelo nem captura sua saída.
- Potência de alimentação não mede energia consumida ou potência irradiada.
- Recomendações exigem revisão humana; não existe atuação sobre equipamentos.
