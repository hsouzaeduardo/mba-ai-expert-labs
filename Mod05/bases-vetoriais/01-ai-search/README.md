# 01 — Onde o vetor mora: Azure AI Search

Notebook: `demo-ai-search.ipynb`

## O que mostra

Os vetores do acervo fictício da Contoso Industrial (`Cap05/acervo/`) guardados num índice dedicado do Azure AI Search, no mesmo roteiro das outras cinco bases de `bases-vetoriais`, para comparar lado a lado: preparar os vetores → criar a estrutura vetorial → gravar → buscar → RAG completo.

- **Slides 20 e 21:** a pergunta que decide onde o vetor mora é "o dado muda em tempo real?". Acervo estável pede um índice dedicado.
- **Slide 22:** a linha do AI Search: até 4.096 dimensões, HNSW e KNN exaustivo, reranking, "acervo grande e estável; híbrido e reranking sem código".
- **Slide 23:** HNSW (aproximado, em memória) contra KNN exaustivo (exato), na mesma pergunta e com o mesmo vetor de consulta.

## Pré-requisitos no Azure

- **Azure AI Search** em qualquer tier. A busca vetorial roda até no Free (limitado a 3 índices e 50 MB); o serviço Basic de `tipos-de-rag` serve. Use a **chave de administração**: o notebook cria o índice `cap05-base-vetorial`. Não há opção a habilitar; só serviços criados antes de janeiro de 2019 podem não aceitar índice vetorial.
- **Azure OpenAI** com um deployment de embedding (`text-embedding-3-small` no `.env.example`) e um deployment de chat (por exemplo, `gpt-5-mini`).
- Não depende de `tipos-de-rag/00`: o índice daqui é próprio, e o `cap05-acervo` não é tocado.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS`, `AZURE_SEARCH_ENDPOINT` e `AZURE_SEARCH_API_KEY`.

Copie `Cap05/.env.example` para `Cap05/.env` e preencha. O que faltar é perguntado na hora da execução. Não grave chaves no notebook.

## Como rodar

1. Instale as dependências com `pip install -r Cap05/requirements.txt` ou rode a célula `%pip` do notebook.
2. Abra o notebook nesta pasta e execute todas as células, em ordem.
3. Rodar de novo é seguro: o índice é atualizado e os trechos são regravados pelo mesmo `id`, sem duplicar.

## O que observar

- **Execução 2:** o serviço registra os dois algoritmos, mas só o `hnsw` é usado pelo campo. O `knn-exaustivo` fica declarado, sem perfil; a busca exata da Execução 4 usa o parâmetro de consulta `exhaustive=True`, que vale no próprio campo HNSW.
- **Execução 4:** os SKUs 48213-B, C e D tendem a quase empatar, como no slide 14 (veja a coluna `diferença para o 1º`): trocar a base não muda a natureza do vetor. A coluna `similaridade` é o `@search.score` (`1 / (1 + distância de cosseno)`, de 0,333 a 1); as colunas `cosseno` e `diferença para o 1º` estão na escala do cosseno, a que se compara com as outras bases.
- **Execução 4:** na comparação HNSW x exaustivo, a pergunta do SKU vira vetor uma vez, e o mesmo vetor vai às duas buscas: só o algoritmo muda. Com 50 trechos, o HNSW e o exaustivo tendem a devolver o mesmo top 5 (recall@5 = 5/5). Busca vetorial é aproximada por definição; o exaustivo é o gabarito para medir o recall quando o acervo cresce.
- Os números mudam com o modelo e a dimensão do embedding e podem variar entre execuções. Por isso o notebook mostra posições e similaridades.

## Limpeza

A última célula apaga só o índice `cap05-base-vetorial` quando `APAGAR_RECURSOS = True`; o `cap05-acervo` e o serviço continuam. Apagar o índice não reduz a fatura: num tier dedicado, o serviço cobra por hora enquanto existir, e só apagar o serviço para a cobrança (confira antes se `tipos-de-rag` ainda vai usá-lo).
