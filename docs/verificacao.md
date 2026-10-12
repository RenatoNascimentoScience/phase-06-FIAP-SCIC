# Verificação da implementação

## Resultado

- 40 testes passaram no pacote extraído, usando um ambiente virtual novo com as
  dependências de `requirements.txt` instaladas isoladamente.
- O script de demonstração executou a partir de outro diretório, por caminho
  absoluto, com leitura correta do CSV.
- O menu anterior foi percorrido com entradas simuladas: opções 1 a 4 e
  encerramento funcionaram; as quatro opções provisórias foram preservadas.
- O modelo anterior reproduziu MAE 8,15 ms, MSE 81,51 ms², RMSE 9,03 ms e
  R² 0,9375, com 36 registros de treino e 12 de teste.
- A heap contém dez registros; `com` e `MED` retornam oito registros cada;
  ciclo 7 converte para binário 111 e hexadecimal 7; primeiro registro tem 50,40 W.
- O ZIP candidato passou pela verificação de integridade e contém fontes, testes,
  documentos e pendências explícitas, sem histórico Git, ambiente ou caches.
- Os módulos novos não contêm chamadas a entrada ou impressão no terminal.

## Preservação

O código principal e o CSV permanecem byte a byte iguais ao estado anterior.

| Arquivo | SHA-256 |
| --- | --- |
| `codigo_fonte.py` | `a6b32c2f3290bfccb252a224ee6930aefd60488d52d4219f12f24c536faecfe8` |
| `dados_aurora_siger.csv` | `62d89c5fb767d5e35a19b23bcf1b7da7339d36a4621405b7a33545e050543ddc` |

O manifesto de testes registra também hashes das seis funções anteriores de
processamento e consulta. A futura integração do menu pode alterar a navegação,
mas não deve modificar essas funções ou o CSV sem acordo do grupo.

## Pendências para entrega final

1. Integrar as opções 5 a 8 na branch `feat/menu-terminal` e conferir sua navegação.
2. Atualizar README e relatório para refletir o estado integrado.
3. Gravar e publicar o vídeo de até cinco minutos como Não listado.
4. Substituir o conteúdo provisório de `link_video.txt` pelo endereço real e
   conferir duração e acesso manualmente.
5. Gerar o ZIP final e repetir a conferência em uma pasta extraída.

A validação atual comprova os módulos e preservação, não a integração pendente
da interface nem uma publicação no YouTube ou submissão acadêmica.
