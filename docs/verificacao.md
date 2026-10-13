# Verificação da implementação

## Resultado

- O menu foi percorrido com entradas simuladas nas opções 0 a 8, sem erros de
  execução. Nenhuma opção chama mais a mensagem provisória de desenvolvimento.
- Entradas inválidas foram conferidas: opção inexistente, ciclo não numérico,
  prefixo vazio, valor não inteiro e valor negativo na conversão de bases. Em
  todos os casos o sistema não é interrompido e permanece no menu.
- Dos 40 testes automatizados, 39 passam. O teste de preservação das funções
  das opções 1 a 4 falha em cinco delas (`carregar_dados`, `visualizar_dados`,
  `consultar_registros`, `calcular_indicadores_erros` e `executar_modelo_previsao`),
  porque foram alteradas durante a integração do menu e o manifesto
  `tests/preservacao_original.json` mantém os hashes registrados antes dessas
  alterações. O teste do CSV passa.
- O script de demonstração executa a partir de outro diretório, por caminho
  absoluto, com leitura correta do CSV.
- Os módulos de `src/` não contêm chamadas de entrada ou impressão no terminal;
  a interação com o usuário fica em `codigo_fonte.py`.

## Resultados conferidos por opção

| Opção | Resultado com a base fornecida |
| --- | --- |
| 1 | 48 registros, 13 colunas, seis módulos, 12 sensores; 38 ativos, cinco em manutenção e cinco em alerta. |
| 2 | Consultas por módulo, sensor, status e ciclo; `Com` retorna oito registros da Comunicação Central. |
| 3 | Latência média 174,81 ms; erro absoluto médio 9,23 ms; erro relativo médio 4,94%; 38 Baixo, cinco Atenção, cinco Preocupante. |
| 4 | 36 registros de treino e 12 de teste; MAE 8,15 ms, MSE 81,51 ms², RMSE 9,03 ms, R² 0,9375; baseline com MAE 33,44 ms e RMSE 36,98 ms. |
| 5 | Dez registros na heap; COM-01 (ciclo 7) é o primeiro atendimento, seguido de MED-01 (ciclo 7). |
| 6 | Prefixos `com` e `MED` retornam oito registros cada; prefixo vazio é recusado pelo menu. |
| 7 | Ciclo 7 = binário 111 = hexadecimal 7; 255 = 11111111 = FF; primeiro registro 24 V × 2,1 A = 50,40 W e R ≈ 11,43 Ω; maior potência 75,57 W (AGR-02, ciclo 4). |
| 8 | Potência média 40,11 W e máxima 75,57 W; cinco alertas urgentes com justificativa, recomendações, validação humana e limitações. |

## Preservação

O CSV permanece igual ao original:

| Arquivo | SHA-256 |
| --- | --- |
| `dados_aurora_siger.csv` | `62d89c5fb767d5e35a19b23bcf1b7da7339d36a4621405b7a33545e050543ddc` |

O manifesto `tests/preservacao_original.json` registra também os hashes das seis
funções das opções 1 a 4, calculados antes da integração do menu. Durante a
integração, cinco delas receberam correções de textos exibidos e de navegação;
`classificar_erro_relativo` permanece igual.

## Pacote de entrega

`scripts/preparar_entrega.py` não encontra chamadas provisórias no menu. A única
pendência apontada pelo empacotador é a ausência de um link válido em
`link_video.txt`.

## Pendências para a entrega final

1. Gravar e publicar o vídeo de até cinco minutos como Não listado.
2. Substituir o conteúdo provisório de `link_video.txt` pelo endereço real e
   conferir duração e acesso manualmente.
3. Gerar o ZIP final e repetir a instalação e os testes em uma pasta extraída.

A validação não comprova a publicação no YouTube nem a submissão acadêmica.
