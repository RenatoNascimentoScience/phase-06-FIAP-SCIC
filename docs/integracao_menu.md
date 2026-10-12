# Integração das opções 5 a 8

## Responsabilidade e preservação

A integração da interface pertence ao integrante responsável pelo menu. As
funções anteriores de leitura, consulta, indicadores e modelo não devem ser
alteradas. Adicionar apenas imports e chamadas nas opções pendentes, mantendo
o fluxo das opções 1 a 4.

Antes de começar, incorporar as funcionalidades aprovadas na branch
`feat/menu-terminal`. As interfaces estão em `contratos_modulos.md`. A versão
completa dos módulos está reunida na branch `docs/entrega-scic` para revisão;
ela ainda não representa integração aprovada na `main`.

## Imports e chamadas

```python
from src.alertas import FilaAlertas
from src.busca import buscar_por_prefixo
from src.dispositivos import analisar_dispositivos, converter_bases
from src.analise import gerar_analise_final
```

| Opção | Processamento | Apresentação necessária |
| --- | --- | --- |
| 5 | `fila = FilaAlertas(dados)`; `fila.proximo()`, `fila.listar()`, `fila.retirar()` | Quantidade, ordem, próximo registro e justificativa; demonstrar uma retirada. |
| 6 | `buscar_por_prefixo(dados, campo, prefixo)` | Escolher `modulo` ou `codigo_sensor`, pedir prefixo e exibir a tabela retornada. |
| 7 | `converter_bases(valor)`; `analisar_dispositivos(dados)` | Bases do inteiro, unidades, sensores como entrada, terminal como saída e interfaces conceituais. |
| 8 | `gerar_analise_final(dados)` | Contagens, resumo elétrico, alertas, recomendações, validação humana e limitações. |

### Exemplo de preparação dos resultados

```python
fila = FilaAlertas(dados)
ordem = fila.listar()  # Não consome a fila.
urgente = fila.retirar()  # Retorna None se a fila estiver vazia.
sensores = buscar_por_prefixo(dados, "codigo_sensor", "MED")
bases = converter_bases(7)
dispositivos = analisar_dispositivos(dados)
unidades = dispositivos.attrs["unidades"]
sintese = gerar_analise_final(dados)
```

As funções retornam tabelas e dicionários, não texto pronto do terminal. O menu
deverá formatar os números na apresentação e mostrar `urgente['registro']`,
`urgente['criterios']` e `urgente['justificativa']` quando houver um alerta.
Quando um agregado da síntese for `None`, apresentar “Sem observações”, não zero.

## Tratamento da navegação

- Conferir se `dados` está disponível antes das chamadas.
- Tratar `ValueError` e exibir sua mensagem, retornando ao menu.
- Converter o texto informado para inteiro antes de chamar `converter_bases`;
  tratar a falha de conversão. Não aceitar valores negativos.
- Recriar a fila ao carregar novamente a base. Retirar de uma fila só altera essa
  fila, nunca o CSV. Reiniciar a demonstração restaura todos os alertas simulados.
- As opções novas não dependem de executar a opção 3 primeiro.
- Prefixo vazio retorna todos os registros; informar esse comportamento ao usuário.
- Remover as chamadas a `funcionalidade_em_desenvolvimento` nas opções concluídas.
- Manter a avaliação do modelo na opção 4. A opção 8 não recalcula métricas.

## Conferência após integração

Executar `python -B -m unittest discover -s tests -v`; os testes de preservação
permitem alterações na navegação, mas verificam as seis funções anteriores de
processamento e consulta e o CSV. Percorrer as opções 0 a 8, repetir consultas,
recarregar dados, usar entradas inválidas e iniciar o programa por caminho
absoluto a partir de outra pasta. Conferir que não existem mais opções provisórias.
