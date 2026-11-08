# 05 — Onde o vetor mora: Azure Managed Redis

Notebook: `demo-redis.ipynb`

## O que mostra

Os mesmos trechos e vetores do acervo fictício da Contoso Industrial (`Cap05/acervo/`), agora guardados e buscados no **Azure Managed Redis**, com o módulo RediSearch. O roteiro é o mesmo dos outros notebooks de `bases-vetoriais`, para comparar lado a lado: preparar os vetores; criar o índice `idx:cap05` (hashes `cap05:trecho:*`, campo `VECTOR HNSW` FLOAT32 com cosseno, e o `FT.CREATE` que o redis-py monta); gravar com `HSET` pela chave do trecho; buscar com KNN (similaridade = 1 − distância de cosseno, posição do trecho certo e latência); e o RAG completo com citação.

Slides: **20** (a pergunta não é qual banco é o melhor), **21** (o dado muda em tempo real?), **22** (linha do Redis: até 32.768 dimensões, HNSW e Flat, sem reranking, "latência de milissegundos, com conjunto que cabe em memória") e **23** (HNSW, o grafo em memória).

## Pré-requisitos no Azure

- **Azure OpenAI** com um deployment de embedding (`text-embedding-3-small` no `.env.example`) e um de chat.
- **Azure Managed Redis** num tier em memória (Memory Optimized, Balanced ou Compute Optimized; o Flash Optimized não tem RediSearch). Na criação, aba **Advanced**: módulo **RediSearch** e política de cluster **Enterprise**. O RediSearch exige a política Enterprise e a política de remoção **NoEviction** (com memória cheia, a escrita falha em vez de apagar chaves). O módulo não pode ser acrescentado depois.
- **Chave de acesso:** a autenticação por chave vem desligada (o padrão é o Microsoft Entra ID). Ligue **Access Keys Authentication** em **Settings → Authentication → Access keys**, onde ficam as chaves; mudar essa opção derruba as conexões abertas. Em produção, prefira Entra ID com o pacote `redis-entraid`.
- Conexão: host `<cache>.<regiao>.redis.azure.net`, porta **10000**, TLS. Para a aula, um cache sem alta disponibilidade sai mais barato. É só para dev/teste, e só dá para escolher na criação: depois, a alta disponibilidade pode ser ligada, mas não desligada.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS`, `AZURE_REDIS_HOST`, `AZURE_REDIS_PORT` (10000) e `AZURE_REDIS_KEY`. Copie `Cap05/.env.example` para `Cap05/.env` e preencha; o que faltar é perguntado na hora. Não grave chaves no notebook.

## Como rodar

1. `pip install -r Cap05/requirements.txt`, ou a célula `%pip` do notebook.
2. Execute todas as células, em ordem. Não depende de outro notebook.
3. Rodar de novo é seguro: `FT._LIST` evita recriar o índice e o `HSET` pela chave sobrescreve, sem duplicar.

## O que observar

- **Execução 3:** 50 trechos novos na primeira carga e 50 regravados na segunda; `FT.INFO` com 50 documentos no índice (`num_docs`). O `hash_indexing_failures` é um contador acumulado desde a criação do índice: depois de uma carga com outra dimensão, ele continua acima de zero mesmo com os 50 trechos de volta. O `vector_index_sz_mb` pode passar bem dos 300 KB dos vetores crus, porque inclui o grafo HNSW e a memória que o índice reserva em blocos.
- **Execução 4:** o quase empate SKU 48213-B x C x D do slide 14 continua aqui. Trocar a base não muda o vetor; híbrido e reranking são decisões de recuperação (`tipos-de-rag/02` e `03`). A latência é a da consulta KNN, sem o embedding: fora do Azure, quase toda ela é rede.
- Os números variam com o modelo e a dimensão do embedding; por isso o notebook mostra posições e similaridades.

## Se algo der errado

- `O Redis recusou a chave`: chave errada ou autenticação por chave desligada. O redis-py tenta reconectar algumas vezes, então o erro leva alguns segundos.
- `unknown command 'FT._LIST'`: o cache foi criado sem o RediSearch; é preciso outro cache.
- Falha no handshake: o redis-py 8 negocia RESP3 (`HELLO 3`) por padrão. Se o cache recusar, acrescente `protocol=2` no `redis.Redis(...)`.
- `Há trechos fora do índice` na Execução 3 (`num_docs` abaixo de 50): o vetor não tem o `DIM` do índice (a dimensão mudou). O `HSET` não dá erro; o trecho só fica fora da busca. Rode a limpeza e o notebook de novo, com `APAGAR_RECURSOS` de volta em `False`. Já falhas acumuladas com os 50 trechos no índice são de gravações anteriores: o contador não diminui.

## Limpeza

A última célula, com `APAGAR_RECURSOS = True`, apaga o índice (`FT.DROPINDEX`, sem `DD`, só se o `FT._LIST` ainda o mostrar) e os 50 hashes `cap05:trecho:*` (`DEL` pela chave de cada trecho, montada com os `id` do acervo, sem embeddings). Pode rodar duas vezes e, depois de reiniciar o kernel, só precisa da Preparação (seção 0). O resto do cache não é tocado; o cache em si é apagado no portal.

Mudou a dimensão do embedding no `.env`? Reinicie o kernel (o notebook lê o `.env` só uma vez): a Execução 3 vai avisar que há trechos fora do índice. Mudou só o modelo, com a mesma dimensão? Nada falha: reinicie o kernel e rode o notebook inteiro, para regravar os 50 vetores com o modelo novo.

## Referências

- Microsoft Learn: [criar o cache](https://learn.microsoft.com/azure/redis/quickstart-create-managed-redis), [módulos](https://learn.microsoft.com/azure/redis/redis-modules), [arquitetura e políticas de cluster](https://learn.microsoft.com/azure/redis/architecture), [busca vetorial](https://learn.microsoft.com/azure/redis/overview-vector-similarity), [Entra ID e chaves](https://learn.microsoft.com/azure/redis/entra-for-authentication), [host, porta e chaves](https://learn.microsoft.com/azure/redis/how-to-redis-access-data), [tier, memória reservada e NoEviction](https://learn.microsoft.com/azure/redis/plan-tiers-and-capacity), [versão do Redis e atualizações](https://learn.microsoft.com/azure/redis/how-to-upgrade), [escolher um serviço de busca vetorial](https://learn.microsoft.com/azure/architecture/guide/technology-choices/vector-search).
- Comandos (redis.io): [vetores](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/), [indexação](https://redis.io/docs/latest/develop/ai/search-and-query/indexing/), [FT.CREATE](https://redis.io/docs/latest/commands/ft.create/), [FT.SEARCH](https://redis.io/docs/latest/commands/ft.search/), [FT.INFO](https://redis.io/docs/latest/commands/ft.info/), [FT.DROPINDEX](https://redis.io/docs/latest/commands/ft.dropindex/), [FT.HYBRID](https://redis.io/docs/latest/commands/ft.hybrid/) (Redis 8.4 ou superior; o Azure Managed Redis está no 7.4).
