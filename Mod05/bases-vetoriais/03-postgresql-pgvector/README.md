# 03 — Onde o vetor mora: Azure Database for PostgreSQL (pgvector)

Notebook: `demo-postgresql-pgvector.ipynb`

## O que mostra

O acervo fictício da Contoso Industrial (`Cap05/acervo/`) gravado numa tabela comum do PostgreSQL, com a coluna `vector` ao lado das colunas relacionais, e a busca por similaridade com o pgvector. É o mesmo roteiro dos outros notebooks de `bases-vetoriais`: preparar os vetores → criar a estrutura vetorial → gravar → buscar → RAG completo.

- **Slides 20 e 21:** a pergunta que decide onde o vetor mora ("o dado muda em tempo real?"). Aqui o vetor vive junto do dado operacional, no banco que já existe.
- **Slide 22:** a linha PostgreSQL (pgvector): até 16.000 dimensões no tipo `vector`, 2.000 no índice HNSW; HNSW, IVFFlat e DiskANN; sem reranking embutido.
- **Slide 23:** o índice HNSW com `vector_cosine_ops`, comparado ao IVFFlat e ao DiskANN, e o plano de execução, que mostra se a busca foi aproximada (índice) ou exata (tabela inteira).

## Pré-requisitos no Azure

- **Azure OpenAI** com um deployment de embedding (`text-embedding-3-small` no `.env.example`) e um de chat.
- **Azure Database for PostgreSQL, servidor flexível.** As versões 13 a 18 trazem o pgvector 0.8.2. O tier Burstable (B1ms, por exemplo) basta para os 50 trechos da aula; a Microsoft não o recomenda para produção.
- **Extensão `vector` liberada no parâmetro de servidor `azure.extensions`.** No portal: Configurações → Parâmetros (Settings → Parameters) → `azure.extensions` → marque a extensão → Salvar. O nome é `vector`, não "pgvector". Pela CLI: `az postgres flexible-server parameter set --resource-group <grupo> --server-name <servidor> --name azure.extensions --value vector`. O valor é a lista inteira de extensões liberadas: se já houver outras, inclua-as.
- **Rede:** com acesso público, o IP da sua máquina nas regras de firewall do servidor. Com acesso privado (rede virtual), rode o notebook de uma máquina dentro da rede.
- **Usuário:** o administrador criado com o servidor, que é membro de `azure_pg_admin` e pode criar a extensão e a tabela.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS` e `AZURE_POSTGRES_CONNECTION_STRING`, no formato do libpq: `host=<servidor>.postgres.database.azure.com port=5432 dbname=postgres user=<usuario> password=<senha> sslmode=require`.

Copie `Cap05/.env.example` para `Cap05/.env` e preencha. O que faltar é perguntado na hora da execução. A string de conexão carrega a senha: não a grave no notebook. Se a senha tiver espaços, escreva-a entre aspas simples (`password='...'`).

## Como rodar

1. Instale as dependências com `pip install -r Cap05/requirements.txt` ou rode a célula `%pip` do notebook.
2. Abra o notebook nesta pasta e execute todas as células, em ordem. A célula de conexão cria a extensão (`CREATE EXTENSION IF NOT EXISTS vector`) e para com uma mensagem clara se ela não estiver liberada. Se o IP da sua máquina não estiver no firewall do servidor, a recusa é imediata: `no pg_hba.conf entry for host ...` (uma regra nova leva até cinco minutos para valer). Se a rede bloquear a saída pela porta 5432, a conexão desiste em 15 segundos.
3. Rodar de novo é seguro: a tabela e o índice usam `IF NOT EXISTS`, e a carga é um `INSERT ... ON CONFLICT (id) DO UPDATE`.

## O que observar

- **Execução 2:** o banco registra a coluna como `vector(1536)` e mostra dois índices, o B-tree da chave e o HNSW do vetor.
- **Execução 3:** 50 linhas, também na segunda execução, gravadas numa transação só. A contagem já sai certa, sem o atraso do AI Search.
- **Execução 4:** a similaridade é `1 - (embedding <=> pergunta)`. O quase empate dos SKUs 48213-B, C e D continua: trocar a base não muda o vetor. A última linha mostra o plano; com só 50 linhas, ele tende a ser `Seq Scan` (busca exata), não o índice HNSW.
- **Execução 5:** a linha "O trecho certo está entre eles?" separa erro de recuperação de erro de geração (slide 29).
- **Leitura arquitetural:** "Casa relacional, alta dimensão, escala horizontal" (slide 22) e quem opera, monitora e paga.

## Limpeza

A última célula apaga a tabela `cap05_trechos`, e o índice junto, quando `APAGAR_RECURSOS = True`. A extensão `vector` fica no banco. O servidor é cobrado enquanto existir (tier, vCores e armazenamento): o Stop desliga o compute, e o servidor volta a ligar sozinho depois de 7 dias; para zerar o custo, apague o servidor.

Mudou a dimensão do embedding no `.env`? Reinicie o kernel (o notebook lê o `.env` só uma vez): a carga falha com `expected 1536 dimensions, not ...`. Apague a tabela e rode o notebook de novo, com `APAGAR_RECURSOS` de volta em `False`. Mudou só o modelo, com a mesma dimensão? Nada falha, porque `vector(n)` guarda a dimensão, não o modelo: reinicie o kernel e rode o notebook inteiro, para regravar os 50 vetores com o modelo novo (o "reindexar tudo" do slide 10).

## Referências

- Microsoft Learn: [DiskANN no PostgreSQL (`pg_diskann`)](https://learn.microsoft.com/azure/postgresql/extensions/how-to-use-pgdiskann), [conectar com Python (`psycopg`)](https://learn.microsoft.com/azure/postgresql/connectivity/connect-python) e [rede com acesso público: regras de firewall e porta 5432](https://learn.microsoft.com/azure/postgresql/network/concepts-networking-public).
