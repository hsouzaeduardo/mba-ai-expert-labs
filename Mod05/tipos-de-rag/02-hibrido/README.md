# 02 — RAG híbrido: palavra-chave e vetor no mesmo índice

Notebook: `demo-hibrido.ipynb`

## O que mostra

O remédio do slide 14 ("O primeiro degrau: por que busca vetorial pura não basta"): a **busca híbrida** no Azure AI Search, em que o BM25 (palavra-chave) e o vetor consultam o mesmo índice, na mesma requisição, e o RRF (Reciprocal Rank Fusion) funde as duas listas. É a linha **Híbrido** do slide 15 (custo "quase o mesmo") e o degrau 1 do slide 17; o slide 13 manda começar por aqui.

1. **Como o índice enxerga códigos:** `analyze_text` com o analisador `pt-BR.lucene` mostra os tokens de "SKU 48213-B", "NR-12 rev. 3" e "projeto ATLAS".
2. **Três consultas, o mesmo índice:** texto (BM25), vetor (a mesma `buscar_vetorial` do notebook 01) e híbrido, nas seis perguntas do slide 14, com a posição do trecho certo em cada uma.
3. **Lupa na string exata:** o top 5 de cada consulta para o SKU 48213-B, lado a lado, e por que o score do híbrido (RRF) é tão pequeno.
4. **RAG completo:** resposta com citação a partir dos 3 primeiros trechos da busca híbrida.

## Pré-requisitos no Azure

- O índice `cap05-acervo`, criado pelo notebook `../00-indice-compartilhado`. Se ele não existir, a célula de configuração para com uma mensagem clara.
- **Azure OpenAI** com o mesmo deployment de embedding usado no notebook 00 e um deployment de chat (por exemplo, `gpt-5-mini`).
- **Azure AI Search:** o mesmo serviço do notebook 00, com a chave de administração do `.env`. O híbrido não pede nada novo no índice: os campos de texto já foram criados pesquisáveis, com `pt-BR.lucene`. Este notebook só consulta e não cria nada.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS` (os mesmos valores do notebook 00), `AZURE_SEARCH_ENDPOINT` e `AZURE_SEARCH_API_KEY`.

Os valores vêm de `Cap05/.env`, uma cópia preenchida do `.env.example`. O que faltar é perguntado na hora da execução.

## Como rodar

1. Rode antes o notebook 00. Uma vez basta: o índice fica no serviço.
2. Abra este notebook e execute todas as células, em ordem.

## O que observar

- **Execução 1:** o hífen separa "48213-B" em `48213` e `b`, e a pergunta passa pelo mesmo analisador. O BM25 compara esses tokens exatamente; o embedding só aproxima.
- **Execução 2:** o texto tende a acertar código, sigla e número; o vetor, paráfrase e sinônimo; o híbrido tende a acertar os dois. Quando o texto acerta uma paráfrase, costuma ser carona em palavras que pergunta e trecho dividem por acaso ("dias", "ferramenta"). Num acervo pequeno como este, as três colunas podem dar 1º em quase tudo; nesse caso, procure a diferença nos scores da lupa (Execução 3).
- **Execução 3:** os scores das três consultas não se comparam. O do híbrido é o do RRF: cada lista dá 1/60 ao 1º, 1/61 ao 2º, e assim por diante, e o trecho soma o que recebeu das duas. Perto de 0,03 é um ótimo resultado, não um defeito. Dentro de cada coluna, compare o 48213-B com os irmãos 48213-C e 48213-D: o BM25 tende a separá-lo com folga, e o vetor, a deixar os três quase empatados.
- **Execução 4:** confira a linha "O trecho certo está entre eles?" antes de julgar a resposta. O prazo certo do SKU 48213-B é 18 dias úteis.
- Os números mudam com o modelo de embedding e com a redação da pergunta. Por isso o notebook mostra posições e scores, e não um ranking fixo.
- O próximo degrau, quando o trecho certo vem fora dos primeiros, é o reranking: notebook `../03-hibrido-com-reranking`.

## Limpeza

Nada a apagar: este notebook não cria recursos. O índice é apagado pela célula de limpeza do notebook 00.
