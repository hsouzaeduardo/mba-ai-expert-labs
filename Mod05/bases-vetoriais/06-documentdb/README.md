# 06 — Onde o vetor mora: Azure DocumentDB

Notebook: `demo-documentdb.ipynb`

## O que mostra

O acervo fictício da Contoso Industrial (`Cap05/acervo/`) guardado numa coleção do **Azure DocumentDB** (compatível com MongoDB), com o vetor como mais um campo de cada documento, e a mesma busca e o mesmo RAG dos outros notebooks da série `bases-vetoriais`.

- **Slides 20 e 21:** a pergunta que decide onde o vetor mora: o dado muda em tempo real?
- **Slide 22:** a linha DocumentDB (API Mongo): até 16.000 dimensões, IVFFlat, HNSW e DiskANN, sem reranking. A escolha certa quando o time já vive em Mongo.
- **Slide 23:** os três algoritmos de índice (recall, memória e dado que muda), e o tier que cada um exige.
- **Slide 14:** o quase empate do SKU 48213-B continua, porque trocar de base não muda o vetor.

## Pré-requisitos no Azure

- **Azure OpenAI** com um deployment de embedding (`text-embedding-3-small` no `.env.example`) e um de chat (por exemplo, `gpt-5-mini`).
- **Azure DocumentDB** (o antigo Azure Cosmos DB for MongoDB vCore):
  - **Tier:** o índice padrão do notebook (IVF, `TIPO_INDICE = "vector-ivf"`) roda em qualquer tier, inclusive no Free: segundo a página do Free tier, só HNSW e DiskANN ficam de fora. HNSW e DiskANN exigem **M30 ou superior**: o Free, o M10, o M20 e o M25 não oferecem esses dois. Algumas páginas do Learn falam em M40 para os dois: teste antes da aula. Se o `createIndexes` ou a busca responderem "not enabled for this cluster", volte para `vector-ivf` ou suba o tier.
  - **Rede:** o IP da sua máquina liberado no firewall do cluster (aba Networking, **+ Add current client IP address**).
  - **Usuário:** o administrador nativo do cluster, com a senha definida na criação (autenticação SCRAM-SHA-256, a da string de conexão).
  - **Feature flag:** nenhuma para a busca vetorial, segundo a documentação atual. A busca de texto completo (BM25), citada na leitura arquitetural, está em gated preview e não é usada aqui.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS` e `AZURE_DOCUMENTDB_CONNECTION_STRING`.

Copie `Cap05/.env.example` para `Cap05/.env` e preencha. A string de conexão vem do portal (menu **Connection strings** do cluster) sem a senha: troque `<password>` pela senha do usuário. Se a senha tiver `@`, `:`, `/` ou `%`, codifique-a antes com `urllib.parse.quote_plus`. O que faltar é perguntado na hora da execução. Não grave chaves no notebook.

## Como rodar

1. Instale as dependências com `pip install -r Cap05/requirements.txt` ou rode a célula `%pip` do notebook.
2. Abra o notebook nesta pasta e execute todas as células, em ordem. Ele cria o banco `cap05`, a coleção `trechos` e o índice vetorial `idx_vetor`.
3. Rodar de novo é seguro: o índice só é recriado se a definição mudar (algoritmo ou parâmetro, como `numLists`), e os trechos são regravados pelo mesmo `_id`, sem duplicar. Se mudar a dimensão do embedding no `.env`, reinicie o kernel (o notebook lê o `.env` só uma vez): a Execução 2 para com um aviso, porque os vetores já gravados têm o tamanho antigo. Rode a limpeza e depois o notebook inteiro, com `APAGAR_RECURSOS` de volta em `False` (é o "reindexar tudo" do slide 10). Mudou só o modelo, com a mesma dimensão? Nada falha: reinicie o kernel e rode o notebook inteiro, para regravar os 50 vetores com o modelo novo.
4. Para ver HNSW ou DiskANN num cluster M30 ou superior, troque `TIPO_INDICE` na Execução 2 e rode o notebook de novo a partir dela. O índice novo pode levar alguns minutos para ficar pronto: se a Execução 4 avisar que a busca voltou vazia, espere e rode-a de novo. Num tier que não aceite esses dois, o `createIndexes` falha: a Execução 2 recria o índice anterior e para com um aviso, e a busca continua com ele. Volte `TIPO_INDICE` para `"vector-ivf"` ou suba o tier.

## O que observar

- **Execução 2:** o índice vetorial é um comando (`createIndexes` com `cosmosSearch`), e a tabela mostra como o serviço o registrou.
- **Execução 3:** 50 documentos na coleção; numa segunda execução, 0 novos e 50 substituídos.
- **Execução 4:** com `COS`, o `searchScore` já é a similaridade de cosseno (maior = mais próximo), sem conversão. No SKU 48213-B, os irmãos B, C e D tendem a quase empatar: trocar a base não conserta a recuperação.
- **Execução 5:** a resposta com citação é a mesma dos outros notebooks; só mudou o lugar onde o vetor mora.

## Limpeza

A última célula apaga a coleção `trechos`, e com ela o índice `idx_vetor`, quando `APAGAR_RECURSOS = True`. O cluster não é criado pelo notebook: apague-o no portal quando não precisar mais dele, porque fora do Free tier ele cobra enquanto existir.
