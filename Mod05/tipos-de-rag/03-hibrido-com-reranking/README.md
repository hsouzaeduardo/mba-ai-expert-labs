# 03 — Híbrido com reranking: onde a precisão sobe mais por menos esforço

Notebook: `demo-hibrido-com-reranking.ipynb`

## O que mostra

O **semantic ranker** do Azure AI Search ligado sobre a mesma busca híbrida do notebook 02 (BM25 e vetor na mesma consulta, fusão RRF). É a linha **Híbrido com reranking** do slide 15, o funil do slide 16 (50 candidatos → nota de 0 a 4 → 5 trechos no contexto) e o degrau 2 do slide 17.

1. **O mesmo híbrido, agora com semantic ranker:** a mesma consulta com `query_type="semantic"` e `semantic_configuration_name="semantica-padrao"`, mais um terceiro parâmetro, opcional, de plano B: `semantic_error_mode="partial"`. Para a pergunta do gabarito sobre a passagem do marido, mostra a posição do trecho certo antes e depois e o top 5 com o score RRF e a nota do reranker.
2. **Antes e depois:** as seis perguntas do slide 14 e a pergunta do reranking. O trecho certo entra no top 5?
3. **O funil do slide 16:** quantos dos 50 candidatos têm nota 3 ou mais, entre 2 e 3 e abaixo de 2.
4. **Contexto enxuto e fatura:** tokens (`o200k_base`) de 20 trechos do híbrido contra 5 reordenados, e a resposta com citação a partir dos 5.

## Pré-requisitos no Azure

- O índice `cap05-acervo`, criado pelo notebook `../00-indice-compartilhado`, que já traz a configuração semântica `semantica-padrao`. Se o índice não existir, a célula de configuração para com uma mensagem clara.
- **Azure AI Search** no tier **Basic ou superior**, numa região com semantic ranker. Todo serviço começa no plano gratuito do semantic ranker, com cota mensal de consultas (a página de preços fala nas 1.000 primeiras do mês). Esgotada a cota, a consulta semântica devolve erro de cobrança até o serviço passar para o plano Standard, pago por uso, na página **Premium features** do serviço, no portal do Azure.
- Uma execução completa do notebook faz **8 consultas semânticas** (1 na Execução 1 e 7 na Execução 2).
- **Azure OpenAI** com o mesmo deployment de embedding do notebook 00 e um deployment de chat (por exemplo, `gpt-5-mini`).
- Este notebook só consulta e não cria nada.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS` (os mesmos valores do notebook 00), `AZURE_SEARCH_ENDPOINT` e `AZURE_SEARCH_API_KEY`.

Os valores vêm de `Cap05/.env`, uma cópia preenchida do `.env.example`. O que faltar é perguntado na hora da execução.

## Como rodar

1. Rode antes o notebook 00. Uma vez basta: o índice fica no serviço.
2. Abra este notebook e execute todas as células, em ordem.

## O que observar

- `buscar_com_reranking` é `buscar_hibrida` com dois parâmetros a mais (e um terceiro, opcional, de plano B: `semantic_error_mode`): configuração, não reengenharia (slide 16). Nada muda no chunking, no embedding ou no índice.
- Ensaie antes da aula: neste acervo pequeno, o híbrido pode já pôr o trecho certo no top 5 (linhas **sim → sim** na Execução 2). A lição, então, está na mudança de posição, na nota do reranker e no contexto menor da Execução 4.
- O `@search.score` do híbrido é o score RRF, perto de 0,03 no máximo. A nota do reranker vai de 0 a 4 e decide a ordem.
- O reranker só reordena os 50 candidatos: se o trecho certo não estiver entre eles, ele não aparece.
- Um “—” no lugar da nota quer dizer que a etapa semântica não rodou (fila cheia ou falha passageira). Com `semantic_error_mode="partial"`, a consulta devolve a ordem do híbrido em vez de erro.
- As notas variam um pouco entre execuções e com atualizações do modelo de ranking. Leia posições e faixas de nota, não casas decimais.

## Limpeza

Nada a apagar: este notebook não cria recursos. O índice é apagado pela célula de limpeza do notebook 00.
