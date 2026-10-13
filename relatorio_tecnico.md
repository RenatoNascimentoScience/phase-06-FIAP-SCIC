# Relatório técnico — SCIC Aurora Siger

## 1. Contexto e objetivo

O Sistema de Comunicação Interplanetária da Colônia organiza informações
operacionais da Aurora Siger para apoiar decisões sobre comunicação. O protótipo
carrega uma base simulada, compara estimativas e observações, avalia regressão,
prioriza alertas e permite consultas por prefixo. Seus resultados são apoio à
decisão, não comandos automáticos para equipamentos.

O desenvolvimento utiliza os conteúdos da fase 06: estruturas de dados,
precisão numérica, avaliação de modelos, dispositivos, bases numéricas,
eletricidade, gerenciamento inteligente e responsabilidade social. O enunciado
permite simulação e não exige infraestrutura real ou serviços externos.

O sistema é executado por um menu no terminal (`codigo_fonte.py`) com oito
opções integradas. Os cálculos de heap, trie, bases numéricas, potência e síntese
ficam em módulos de `src/`, que apenas recebem dados e retornam resultados; o
menu lê as entradas do usuário e apresenta as saídas.

| Opção | Funcionalidade | Seção |
| --- | --- | --- |
| 1 | Carregar e Visualizar Dados | 2 |
| 2 | Consultar Registros | 2 |
| 3 | Calcular Indicadores e Erros | 3 |
| 4 | Executar Modelo de Previsão | 4 |
| 5 | Analisar Alertas por Prioridade (heap) | 5 |
| 6 | Buscar Registros por Prefixo (trie) | 6 |
| 7 | Bases Numéricas e Dados Elétricos | 7 |
| 8 | Análise Geral do Sistema | 8 |

## 2. Dados e organização

`dados_aurora_siger.csv` contém 48 registros, 13 campos, seis módulos, 12 sensores
e oito ciclos. A demonstração contempla Comunicação Central, Habitação Alfa,
Agricultura Hidropônica, Laboratório Científico, Suporte Médico e Armazenamento
de Dados. Há 38 registros ativos, cinco em manutenção e cinco em alerta.

| Campo | Significado e unidade |
| --- | --- |
| `ciclo` | Ordem discreta do cenário; não contém duração física. |
| `modulo`, `tipo_modulo` | Identificação e finalidade do módulo. |
| `codigo_sensor` | Identificador textual do sensor; não é um número hexadecimal. |
| `latencia_prevista_ms`, `latencia_observada_ms` | Estimativa e observação simuladas, em milissegundos. |
| `tensao_v`, `corrente_a` | Alimentação elétrica em volts e amperes. |
| `status` | Ativo, Manutencao ou Alerta. |
| `prioridade`, `criticidade` | Escalas internas; números maiores indicam maior urgência. |
| `modulo_essencial` | Indicador 0/1 de importância operacional. |
| `mensagem_alerta` | Descrição resumida da condição simulada. |

A leitura (opção 1) e as consultas por módulo, sensor, status ou ciclo (opção 2)
utilizam Pandas. Os módulos de `src/` trabalham com cópias ou resultados
independentes e não reescrevem o CSV. As validações verificam colunas necessárias
e valores compatíveis com cada operação.

Essas latências representam comunicação operacional simulada na colônia.
Não são estimativas do tempo de viagem de sinais entre Terra e Marte.

## 3. Indicadores e erros numéricos

A opção 3 calcula potência aproximada, latência média e erros:

$$
P=V\cdot I,\qquad E_a=|L_{observada}-L_{prevista}|,
\qquad E_r=\frac{E_a}{L_{observada}}\cdot100\%.
$$

A observação foi escolhida como referência do erro relativo. Isso precisa ser
explicitado: escolher a previsão no denominador responderia a outra comparação.
O erro absoluto conserva milissegundos; o relativo é um percentual.

No registro MED-01 do ciclo 7, a previsão é 154 ms e a observação 215 ms.
O erro absoluto é 61 ms e o relativo aproximadamente 28,37%. A estimativa
subestimou a observação; o módulo médico é essencial e deve receber atenção.

Na base completa, a opção 3 apresenta latência média de 174,81 ms,
erro absoluto médio de 9,23 ms e erro relativo médio de 4,94%. Os limites
internos são: até 5% “Baixo”; acima de 5% até 15% “Atenção”; acima de 15%
“Preocupante”. A classificação resulta em 38, cinco e cinco registros,
respectivamente. Esses limites não constituem padrões físicos universais.

O exemplo `0.1 + 0.2` ilustra representação binária aproximada. Arredondar facilita
a leitura, mas não elimina erros de medição ou de previsão. Os desvios de dezenas
de milissegundos da base não devem ser atribuídos ao arredondamento computacional.

O cálculo não trata observação zero: nesse caso o percentual é
matematicamente indefinido. A base fornecida não contém essa condição, e a
limitação permanece documentada.

## 4. Modelo simples e avaliação

O modelo da opção 4 é uma regressão linear do scikit-learn, com entradas
`latencia_prevista_ms`, `tensao_v`, `corrente_a` e `ciclo`; o alvo é
`latencia_observada_ms`. A divisão utiliza 36 registros para treino e 12 para
teste, com `random_state=42`. O baseline prevê a média da latência do treino.

Resultados da execução da opção 4, no ambiente registrado nas evidências:

| Métrica | Regressão | Baseline da média do treino |
| --- | ---: | ---: |
| MAE | 8,15 ms | 33,44 ms |
| MSE | 81,51 ms² | Não apresentado pela opção 4 |
| RMSE | 9,03 ms | 36,98 ms |
| R² | 0,9375 | Não apresentado pela opção 4 |

MAE expressa o desvio absoluto médio; MSE penaliza desvios maiores e possui
unidade quadrática; RMSE retorna à unidade do alvo. R² compara o erro quadrático
com a variação da resposta no teste, não mede uma “acurácia de comunicação”.

A regressão superou o baseline nessa divisão. Um R² alto não torna o modelo
perfeito. RMSE normalmente é maior ou igual ao MAE; a diferença observada não
prova, sozinha, a presença de erros extremos. Uma investigação posterior deveria
examinar resíduos e situações críticas separadamente.

A amostra é pequena e simulada. Registros dos mesmos módulos e de diferentes
ciclos são distribuídos aleatoriamente; isso não valida previsão temporal de
ciclos futuros. A base também não documenta quando cada entrada ficaria disponível
numa operação real: tensão e corrente medidas no próprio ciclo não podem ser
assumidas como conhecidas antes dele. As métricas avaliam o cenário construído,
não uma implantação real. Não foram adicionados modelos ou buscas de parâmetros.

## 5. Priorização com heap

A opção 5 utiliza `FilaAlertas` (`src/alertas.py`), baseada em `heapq`. Entram registros em Alerta ou Manutencao, formando
dez itens na base. A chave compara maior prioridade, maior criticidade, módulo
essencial, ciclo mais antigo e ordem de inserção. Os três primeiros valores têm
o sinal invertido porque `heapq` organiza o menor elemento na raiz.

A sequência de inserção resolve empates e impede comparar dicionários. O critério
final representa a ordem do CSV, não uma chegada real medida. Um erro relativo
maior não substitui silenciosamente essa política: prioridade é uma regra
declarada e deve ser revisada quando a situação exigir.

Os cinco primeiros atendimentos são COM-01/ciclo 7, MED-01/ciclo 7,
DAT-02/ciclo 8, AGR-02/ciclo 4 e LAB-01/ciclo 5. Os dois primeiros têm prioridade
5, criticidade 5 e são essenciais; o empate é resolvido pela ordem original.
Cada resultado apresenta seus critérios e sua justificativa. No menu, a opção 5
exibe o alerta mais urgente, a fila completa na ordem de atendimento e a
vantagem da heap sobre uma lista simples.

Consultar a raiz custa O(1); inserir ou retirar custa O(log n); construir a fila
por `heapify` custa O(n). Uma lista simples precisaria ser percorrida para localizar
o próximo item se não estivesse previamente organizada. Listar todos os alertas
tem custo O(n log n) e utiliza uma cópia; a heap não é uma lista inteiramente
ordenada. O CSV permanece intacto após as retiradas.

## 6. Busca com trie

A opção 6 permite escolher entre nome do módulo e código do sensor e informar
um prefixo; a busca é feita por `buscar_por_prefixo` (`src/busca.py`).
A trie compartilha caminhos de caracteres de nomes e códigos. Os nós terminais
guardam posições dos registros. A busca percorre o prefixo e seus descendentes;
as posições são reunidas sem repetição e ordenadas para preservar a ordem da base.
Índices repetidos do Pandas não confundem essa associação.

Caixa, acentos e espaços excedentes são normalizados somente no índice e na
pesquisa. As palavras apresentadas não são reescritas. O prefixo `com` encontra
oito registros da Comunicação Central e `MED` encontra oito registros de sensores
médicos. Prefixo inexistente retorna tabela vazia. No módulo, prefixo vazio retorna todos
os registros indexados; o menu recusa essa entrada e pede ao menos um caractere.
Essa consulta não busca fragmentos no meio das palavras.

Localizar o nó depende do tamanho do prefixo. Enumerar a subárvore, reunir e
ordenar resultados também custa trabalho; não há retorno de milhares de registros
em tempo constante. O índice é reconstruído para cada base recebida, privilegiando
coerência e simplicidade neste cenário pequeno.

## 7. Dispositivos, bases e eletricidade

A opção 7 reúne três partes em um submenu: conversão entre bases, dados
elétricos e dispositivos de entrada e saída.

**Dispositivos.** Sensores ou medidores poderiam fornecer tensão, corrente e
latência. Nesta implementação, o CSV simula essa entrada e o teclado permite ao
operador navegar e consultar. Terminal e relatório são saídas; num sistema real,
um painel de monitoramento ou alarmes cumpririam esse papel. Rede cabeada, Wi-Fi,
Bluetooth e USB são interfaces conceituais de coleta e comunicação local, não
implementações completas do enlace interplanetário.

**Bases numéricas.** O menu exibe os oito ciclos da base em decimal, binário e
hexadecimal e converte um inteiro informado pelo usuário. O ciclo 7 resulta em
binário 111 e hexadecimal 7; decimal 26 resulta em binário 11010 e hexadecimal
1A; decimal 255 resulta em binário 11111111 e hexadecimal FF. `converter_bases`
rejeita negativos, floats, textos e booleanos, e o menu trata entradas inválidas.
O hexadecimal agrupa quatro bits por dígito, tornando identificadores mais curtos;
por exemplo, o número do sensor COM-01 pode ser armazenado como binário 00000001
ou hexadecimal 0x01. O código textual do sensor, porém, não é um número hexadecimal.

**Eletricidade.** `analisar_dispositivos` calcula potência em uma cópia. No
primeiro registro, P = V × I = 24 V × 2,1 A = 50,40 W. A média dos registros é
aproximadamente 40,11 W e o maior valor, 75,57 W, ocorre no registro AGR-02 do
ciclo 4, com 22,9 V, 3,3 A e status Alerta. O menu também apresenta médias por
módulo; Agricultura Hidropônica tem a maior potência média (69,24 W) e Habitação
Alfa, a menor (17,09 W). Não somar potências de ciclos diferentes como se fossem
consumo energético.

A lei de Ohm é aplicada no menu como resistência equivalente, R = V / I: no
primeiro registro, 24 V / 2,1 A ≈ 11,43 Ω. Esse valor descreve a carga vista pela
alimentação naquele instante; o transmissor não foi modelado como resistor ideal.

O cálculo representa potência de alimentação em corrente contínua. Energia em
Wh exigiria duração; potência irradiada exigiria informações sobre o transmissor,
eficiência e antena. Quedas de tensão ou aumentos de corrente podem indicar
sobrecarga ou falha de alimentação, mas não comprovam sozinhos a causa de uma
latência alta.

## 8. Síntese e gerenciamento inteligente

A opção 8 apresenta a síntese gerada por `gerar_analise_final` (`src/analise.py`):
contagens, cinco alertas urgentes, resumo elétrico, recomendações, gerenciamento
inteligente, validação humana e limitações. Cada recomendação aponta sensor, ciclo e observações que a sustentam.
Não recalcula a regressão nem interpreta texto impresso pela opção 4.

No caso médico do ciclo 7, a latência de 215 ms, a estimativa de 154 ms e a
alimentação de 10,9 V justificam conferir sensor, enlace e alimentação. A tensão
mais baixa não prova a causa do atraso. Por ser um módulo essencial, avaliar
conceitualmente um enlace alternativo é uma proposta de planejamento, sujeita
à disponibilidade e validação humana.

Monitoramento contínuo poderia comparar leituras novas, detectar falta de dados
recentes e observar recorrência. Histórico e armazenamento preservariam evidências
para inspeção e manutenção. Esta base não contém rótulos de falhas nem histórico
suficiente para alegar manutenção preditiva treinada.

A heap automatiza a organização do atendimento e a trie facilita acesso local.
Nenhuma implementa transporte, confirmação de entrega ou telecomando.
Redundância precisa considerar falhas comuns aos enlaces. Uma microrrede poderia
coordenar geração e reserva para manter comunicação, mas autonomia exigiria
medidas adicionais de energia, duração e disponibilidade.

## 9. Reflexão social, cultural e sustentável

**Sustentabilidade.** Priorizar alertas relevantes e consultar registros específicos
pode orientar comunicação e inspeções mais eficientes. O protótipo apresenta
potência e prioridades, mas não mede economia de energia. Uma decisão responsável
precisa avaliar consumo ao longo do tempo, manutenção e vida útil dos dispositivos,
sem anunciar ganhos ambientais não demonstrados.

**Diversidade cultural e prevenção de exclusão.** As regras de atendimento usam
condições operacionais, não origem cultural ou estilo linguístico da mensagem.
Normalizar acentos no índice facilita localizar registros sem alterar sua escrita.
Uma mensagem não padronizada não deve perder prioridade por sua forma de expressão.
Os impactos das regras precisam ser avaliados com os usuários, respeitando a
diversidade de experiências afro-brasileiras e indígenas, sem tratá-las como
grupos homogêneos ou fontes genéricas de exemplos decorativos.

**Transparência e responsabilidade humana.** Exibir critérios da heap permite
entender por que COM-01 aparece antes de MED-01, mesmo quando o desvio médico
é maior. O operador deve poder questionar o desempate, revisar evidências e
registrar a decisão. O sistema não transfere responsabilidade para o algoritmo;
dados ausentes e hipóteses limitadas devem ser reconhecidos antes da ação.

Esses três pontos conectam a reflexão às escolhas do projeto: eficiência exige
evidência, acesso deve respeitar diferentes formas de comunicação e recomendações
precisam ser explicáveis e revisáveis.

## 10. Testes, limites e melhorias

Os testes cobrem ordem e desempates da heap, cópias independentes, prefixos,
acentos, índices repetidos, conversões, potência, entradas inválidas, síntese
vazia, rastreabilidade das recomendações e preservação das funções das opções 1
a 4 e do CSV. A execução dos módulos está em `docs/evidencias_modulos.json`,
e a conferência do menu em `docs/verificacao.md`. O teste de preservação compara
essas funções com o manifesto `tests/preservacao_original.json`, registrado antes
da integração do menu; por isso, ele aponta as alterações feitas nelas durante
a integração.

Durante a integração, o grupo corrigiu textos exibidos e a navegação das funções
anteriores: a lista de status passou a mostrar a mesma grafia do CSV e um ciclo
inválido não encerra mais a consulta. Limitações remanescentes: a consulta por
módulo utiliza expressão regular, e o erro relativo com referência zero não
possui tratamento específico.

Melhorias possíveis: tratar a consulta por módulo como texto literal, documentar
geração e disponibilidade das variáveis, avaliar ciclos posteriores separadamente,
analisar resíduos por situação, registrar decisões humanas e gerar gráficos das
latências e erros com Matplotlib.

## 11. Entrega e referências

A entrega final reúne código principal, módulos, CSV, README, relatório e
`link_video.txt`, com vídeo de até cinco minutos publicado como Não listado.
O pacote é gerado por `scripts/preparar_entrega.py`, que recusa a versão final
enquanto houver opção provisória no menu ou faltar um link válido.

Referência principal: FIAP, Atividade Integradora — Sistema de Comunicação
Interplanetária da Colônia, transcrição em [scic-instructions.md](scic-instructions.md).
Os capítulos da fase 06 fundamentam complexidade e estruturas (3–4), precisão
(6), avaliação e ferramentas (7–8), dispositivos/bases/eletricidade (9–11),
gerenciamento (12) e reflexão cultural (14). Exemplos e resultados deste relatório
referem-se à base do projeto, não a medições de infraestrutura real.
