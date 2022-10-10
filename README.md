# rinex_subinterval_analyzer

## Estrutura esperada para a pasta "input":

![image](https://user-images.githubusercontent.com/10555891/194937165-ffa41a4d-63db-4e2e-b01d-2e6a03978435.png)

Em que "06_06_2016", por exemplo, é o nome de um ponto.

E "05", "10", etc, se referem aos intervalos de subamostragem.

"base" deve estar presente, e se refere ao processamento obtido com o arquivo completo do rastreamento.

Cada pasta de intervalo de subamostragem deve conter os arquivos gerados para cada segmento individual.
Por exemplo, o conteúdo de uma das pastas "05" poderia ser:

![image](https://user-images.githubusercontent.com/10555891/194937919-abaa4243-de00-444d-ae40-b1d3568c079e.png)

## Configurações iniciais

O caminho para a pasta "input" deve ser especificado no corpo do "analyzer.py" - Linha 15.

O caminho para a pasta onde os resultados ficarão deve ser especificado no mesmo arquivo - Linha 16.

## Executando

Para iniciar a rotina, basta executar o script "main.py".
