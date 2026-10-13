# SCIC — Sistema de Comunicação Interplanetária da Colônia

Protótipo acadêmico da Aurora Siger para organizar registros simulados de
comunicação, analisar latências, avaliar uma previsão simples, priorizar alertas
com heap, consultar registros com trie e relacionar os dados com dispositivos,
bases numéricas e eletricidade básica. O escopo está descrito em
[scic-instructions.md](scic-instructions.md).

## Funcionalidades

O sistema é executado por um menu no terminal (`codigo_fonte.py`). Todas as
opções estão integradas:

| Opção | Funcionalidade | O que faz |
| --- | --- | --- |
| 1 | Carregar e Visualizar Dados | Lê o CSV com Pandas e exibe os primeiros registros, a quantidade de módulos e sensores e a contagem por status. |
| 2 | Consultar Registros | Pesquisa por módulo, sensor, status ou ciclo. |
| 3 | Calcular Indicadores e Erros | Calcula potência (P = V × I), erro absoluto e erro relativo da latência, classifica os erros (Baixo, Atenção, Preocupante) e demonstra a precisão de ponto flutuante. |
| 4 | Executar Modelo de Previsão | Regressão linear (scikit-learn) para prever a latência observada, com divisão treino/teste 75/25, métricas MAE, MSE, RMSE e R² e comparação com um baseline pela média. |
| 5 | Analisar Alertas por Prioridade | Fila de prioridade com heap: mostra o alerta mais urgente e a fila ordenada por prioridade, criticidade, módulo essencial e ciclo. |
| 6 | Buscar Registros por Prefixo | Busca por prefixo com trie em nomes de módulos ou códigos de sensores, ignorando maiúsculas e acentos. |
| 7 | Bases Numéricas e Dados Elétricos | Converte valores entre decimal, binário e hexadecimal; calcula potência e resistência (Lei de Ohm, R = V / I) por módulo; descreve dispositivos de entrada e saída e interfaces de comunicação. |
| 8 | Análise Geral do Sistema | Síntese com contagens, resumo elétrico, cinco alertas mais urgentes, recomendações, gerenciamento inteligente da comunicação, validação humana e limitações. |
| 0 | Encerrar | Finaliza o programa. |

Resultados com a base fornecida: o modelo obtém R² 0,9375, MAE 8,15 ms e RMSE
9,03 ms; a heap prioriza dez registros em alerta ou manutenção, com COM-01
(ciclo 7) como primeiro atendimento; o prefixo `com` retorna oito registros; o
primeiro registro tem 24 V × 2,1 A = 50,40 W.

## Arquivos

| Arquivo ou pasta | Conteúdo |
| --- | --- |
| `codigo_fonte.py` | **Arquivo principal.** Menu do terminal e apresentação das opções 1 a 8. |
| `dados_aurora_siger.csv` | Base simulada: 48 registros, seis módulos, 12 sensores e oito ciclos. |
| `src/alertas.py` | Fila de prioridade de alertas (heap). |
| `src/busca.py` | Índice trie para busca por prefixo. |
| `src/dispositivos.py` | Conversão de bases numéricas e cálculo de potência. |
| `src/analise.py` | Síntese operacional usada na opção 8. |
| `src/_validacao.py` | Validações compartilhadas pelos módulos acima. |
| `tests/` | Testes automatizados dos módulos e verificação de preservação. |
| `scripts/` | Demonstração independente dos módulos e preparação do ZIP de entrega. |
| `docs/` | Contratos dos módulos, guia de integração, evidências e roteiro do vídeo. |
| `relatorio_tecnico.md` | Explicação técnica, resultados, impactos e limitações. |
| `requirements.txt` | Versões verificadas de NumPy, Pandas e scikit-learn. |
| `link_video.txt` | Link da apresentação no YouTube (Não listado). |

Os módulos em `src/` apenas calculam e retornam dados (tabelas e dicionários).
Toda a interação com o usuário — `input()` e `print()` — fica em `codigo_fonte.py`.

## Dependências

Ambiente de referência: Python 3.12.10.

| Biblioteca | Versão | Uso |
| --- | --- | --- |
| NumPy | 2.5.0 | Cálculos numéricos e RMSE. |
| Pandas | 2.3.3 | Leitura do CSV, filtros e agregações. |
| scikit-learn | 1.9.0 | Divisão dos dados, regressão linear e métricas. |

`heapq`, `unittest`, `unicodedata`, `pathlib`, `argparse` e as demais
ferramentas auxiliares pertencem à biblioteca padrão do Python. Não são usadas
bibliotecas fora das estudadas na fase.

## Instalação e execução

No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe codigo_fonte.py
```

Não é necessário ativar o ambiente. Em Linux ou macOS, o executável do ambiente
fica em `.venv/bin/python`.

Execute o programa em um terminal (não na janela Interactive/Jupyter do editor),
pois o menu depende de `input()`. O CSV é localizado a partir da pasta do
projeto, então o programa também funciona quando chamado por caminho absoluto
de outro diretório.

## Testes e demonstração dos módulos

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -B scripts/demonstrar_modulos.py
```

O teste de preservação compara as funções das opções 1 a 4 e o CSV com o
manifesto `tests/preservacao_original.json`, registrado antes da integração do
menu. Como algumas dessas funções foram alteradas durante a integração, esse
teste aponta as diferenças; os demais testes passam. Detalhes em
[docs/verificacao.md](docs/verificacao.md).

Para atualizar as evidências dos módulos:

```powershell
.\.venv\Scripts\python.exe -B scripts/demonstrar_modulos.py --saida docs/evidencias_modulos.json
```

## Preparação do pacote de entrega

```powershell
.\.venv\Scripts\python.exe -B scripts/preparar_entrega.py
```

O comando gera o ZIP em `output/`. O empacotador recusa o pacote final enquanto
houver chamadas provisórias no menu ou faltar um link com formato válido em
`link_video.txt`. Ele não verifica o acesso ao YouTube, a duração do vídeo nem a
configuração Não listado; essas verificações cabem ao grupo. Para gerar um
pacote de revisão antes do vídeo, use `--candidato`.

Antes de submeter, extraia o ZIP em outra pasta, instale as dependências e repita
os testes. Histórico Git, ambientes, caches e temporários não entram no ZIP.

## Relatório e apresentação

Ler [relatorio_tecnico.md](relatorio_tecnico.md) para fórmulas, critérios de
prioridade, interpretação do modelo e reflexão social, cultural e sustentável.
O [roteiro do vídeo](docs/roteiro_video.md) organiza uma apresentação de até
cinco minutos.

## Limitações conhecidas

- Os dados são simulados; milissegundos representam latências operacionais da
  colônia, não o tempo físico de propagação entre planetas.
- A consulta por módulo (opção 2) interpreta expressões regulares; o erro
  relativo com latência observada zero não tem tratamento específico (a base
  fornecida não contém esse caso).
- Prioridades e ciclos são critérios simulados. A ordem do CSV desempata
  registros; não comprova uma ordem real de chegada.
- A regressão foi avaliada em uma divisão pequena, sem validação temporal de
  ciclos futuros. A análise geral (opção 8) não recalcula o modelo.
- A potência calculada é a de alimentação (W); não mede energia consumida (Wh)
  nem potência irradiada pela antena. A resistência R = V / I é equivalente,
  calculada a partir das leituras.
- Recomendações exigem revisão humana; o sistema não atua sobre equipamentos.
