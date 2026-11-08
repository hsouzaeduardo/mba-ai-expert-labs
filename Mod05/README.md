# Cap. 5 — Arquitetura de RAG no Azure: guia de execução dos exemplos

Um exemplo simples por pasta, para os exemplos do deck `Cap05-Arquitetura-de-RAG-no-Azure.pptx`. Cada exemplo é um notebook Jupyter no padrão da demo do Cap. 1: texto em português, execuções numeradas, "O que observar", "Leitura arquitetural" e a frase de fechamento tirada do slide. Todos usam o mesmo acervo fictício, em `acervo/`.

Este guia tem quatro passos: criar os recursos no Azure, preparar a máquina, executar cada exercício e limpar tudo depois da aula. Cada pasta tem também um `README.md` próprio, com mais detalhes e com o que fazer se algo der errado.

> **Cenário 100% fictício.** A Contoso Industrial e todos os documentos, projetos, pessoas e números do acervo existem apenas para fins didáticos.

## Visão geral

| Exercício | Slides | Precisa de | Depende de |
|---|---|---|---|
| `tipos-de-rag/00-indice-compartilhado` | 9 a 12 e 23 | Azure OpenAI + AI Search | — |
| `tipos-de-rag/01-vetorial-puro` | 14 e 15 | Azure OpenAI + AI Search | 00 |
| `tipos-de-rag/02-hibrido` | 13 a 15 e 17 | Azure OpenAI + AI Search | 00 |
| `tipos-de-rag/03-hibrido-com-reranking` | 15 a 17 | Azure OpenAI + AI Search | 00 |
| `tipos-de-rag/04-agentico` | 13, 15 e 17 | Azure OpenAI + AI Search | 00 |
| `tipos-de-rag/05-grafo` | 13, 15 e 17 | Azure OpenAI + AI Search | 00 |
| `ragless/01-contexto-longo` | 18 e 19 | Azure OpenAI (chat) | — |
| `ragless/02-arvore-de-secoes` | 18 e 19 | Azure OpenAI (chat) | — |
| `ragless/03-busca-em-arquivos` | 19 | Azure OpenAI (chat) | — |
| `ragless/04-respostas-prontas` | 18 | Azure OpenAI (chat + embedding) | — |
| `bases-vetoriais/01-ai-search` | 20 a 23 | Azure OpenAI + AI Search | — |
| `bases-vetoriais/02-cosmos-db` | 20 a 23 | Azure OpenAI + Cosmos DB for NoSQL | — |
| `bases-vetoriais/03-postgresql-pgvector` | 20 a 23 | Azure OpenAI + PostgreSQL flexível | — |
| `bases-vetoriais/04-azure-sql` | 20 a 23 | Azure OpenAI + Azure SQL Database | — |
| `bases-vetoriais/05-redis` | 20 a 23 | Azure OpenAI + Azure Managed Redis | — |
| `bases-vetoriais/06-documentdb` | 20 a 23 | Azure OpenAI + Azure DocumentDB | — |

## Passo 1 — Criar os recursos no Azure

Crie tudo num único grupo de recursos: depois da aula, apagar o grupo apaga tudo de uma vez.

**Obrigatórios**, para `tipos-de-rag`, `ragless` e `bases-vetoriais/01-ai-search`:

1. **Azure OpenAI**, com endpoint no formato `https://<recurso>.openai.azure.com` e dois deployments:
   - um de chat que aceite structured outputs (por exemplo, `gpt-5-mini`);
   - um `text-embedding-3-small`.
2. **Azure AI Search**, de preferência no tier Basic, numa região com semantic ranker e agentic retrieval (a Brazil South tem). O semantic ranker e o knowledge base já vêm no plano gratuito, com cota mensal. Passar da cota exige o plano Standard, que só existe do Basic para cima.

**Bases vetoriais**: crie só as que for demonstrar.

3. **Azure Cosmos DB for NoSQL**: ative o "Vector Search for NoSQL API" em *Settings → Features*. A ativação pode levar até 15 minutos, então faça antes da aula.
4. **Azure Database for PostgreSQL, servidor flexível**: o Burstable B1ms basta. Libere a extensão `vector` no parâmetro de servidor `azure.extensions` e o IP da sua máquina no firewall.
5. **Azure SQL Database**: o free tier serve. Libere o IP da sua máquina no firewall do servidor.
6. **Azure Managed Redis**: use um tier em memória (o Flash não serve). Na criação, aba *Advanced*, escolha o módulo **RediSearch** e a política de cluster **Enterprise**; isso não pode ser mudado depois. Depois de criado, ligue a *Access Keys Authentication*.
7. **Azure DocumentDB**: qualquer tier serve, inclusive o Free, porque o índice padrão do notebook é IVF (HNSW e DiskANN exigem M30 ou superior). Libere o IP da sua máquina no firewall.

## Passo 2 — Preparar a máquina

1. Instale o Python 3.10 ou superior. Na pasta `Cap05`, crie um ambiente virtual e instale as dependências:

   ```powershell
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   ```

   Use o ambiente virtual: as células `%pip` dos notebooks atualizam pacotes no ambiente em que rodam, e no Python global isso trocaria, por exemplo, o `azure-search-documents` 11.x pelo 12.

2. Abra a pasta `Cap05` no VS Code, com a extensão Jupyter, e em cada notebook escolha o kernel do `.venv`. Se preferir o Jupyter Lab, registre o ambiente uma vez com `.venv\Scripts\python -m ipykernel install --user --name cap05-rag` e escolha o kernel `cap05-rag`.
3. Para o exercício de Azure SQL, instale o **ODBC Driver 17 ou 18 for SQL Server**. Para conferir: `python -c "import pyodbc; print(pyodbc.drivers())"`.
4. Copie `.env.example` para `.env`, nesta pasta, e preencha só as variáveis dos exercícios que vai rodar. Os notebooks leem o `.env` sozinhos; o que faltar é perguntado na hora. O `.env` guarda chaves: não compartilhe nem versione.

### Onde achar cada valor do `.env`

| Variável | Onde encontrar |
|---|---|
| `AZURE_OPENAI_ENDPOINT` e `AZURE_OPENAI_API_KEY` | Recurso do Azure OpenAI no portal, em *Keys and Endpoint* (Chaves e Ponto de Extremidade). Use o formato `https://<recurso>.openai.azure.com`. |
| `AZURE_OPENAI_DEPLOYMENT` e `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Os **nomes** que você deu aos deployments de chat e de embedding, na lista de deployments do portal do Foundry. |
| `AZURE_OPENAI_EMBEDDING_MODEL` e `AZURE_OPENAI_EMBEDDING_DIMENSIONS` | Deixe os padrões: `text-embedding-3-small` e `1536`. |
| `AZURE_SEARCH_ENDPOINT` | Serviço do AI Search, página *Overview*, campo *Url*. |
| `AZURE_SEARCH_API_KEY` | Serviço do AI Search, *Settings → Keys*: a chave de **administração** primária. |
| `AZURE_COSMOS_ENDPOINT` e `AZURE_COSMOS_KEY` | Conta do Cosmos DB, *Settings → Keys*: o URI e a chave primária. |
| `AZURE_POSTGRES_CONNECTION_STRING` | Monte no formato `host=<servidor>.postgres.database.azure.com port=5432 dbname=postgres user=<admin> password=<senha> sslmode=require`. |
| `AZURE_SQL_CONNECTION_STRING` | Banco do Azure SQL, *Settings → Connection strings*, aba **ODBC**. Troque o nome do driver se a máquina tiver o 17 e coloque a senha. |
| `AZURE_REDIS_HOST`, `AZURE_REDIS_PORT` e `AZURE_REDIS_KEY` | Cache do Redis: o host na página *Overview*, a porta `10000` e a chave em *Settings → Authentication → Access keys*. |
| `AZURE_DOCUMENTDB_CONNECTION_STRING` | Cluster do DocumentDB, *Settings → Connection strings*. Troque `<password>` pela senha do usuário administrador. |

## Passo 3 — Executar cada exercício

**Vale para todos:**

- Abra o notebook, escolha o kernel do `.venv` e execute todas as células, em ordem (*Run All*).
- A primeira célula de código é um `%pip install`. Se o pip avisar que atualizou pacotes, reinicie o kernel e execute de novo.
- Rodar de novo é seguro: nada é duplicado.
- A última célula é a limpeza e vem desligada (`APAGAR_RECURSOS = False`).
- Os resultados de embedding, busca e LLM variam de uma execução para outra. Por isso os notebooks mostram posições e scores, sem prometer um ranking fixo. Ensaie cada exercício uma vez antes da aula.

### Tipos de RAG (slides 13 a 17)

Rode o `00` primeiro: ele cria o índice que os outros cinco consultam. Depois, os exercícios 01 a 05 podem rodar em qualquer ordem.

**00 — Índice compartilhado.** A trilha de indexação: chunking por estrutura, embedding e o índice.
- **Cria:** o índice `cap05-acervo`, com os 50 trechos do acervo.
- **Deve aparecer:**
  - 50 trechos de 14 documentos;
  - a tabela de campos que o serviço registrou;
  - a contagem do índice igual a 50;
  - uma busca por "reembolso" devolvendo resultados.
- **Limpeza:** só no fim da aula, porque os notebooks 01 a 05 dependem do índice. Se rodou o 04, rode antes a limpeza dele.

**01 — Vetorial puro.** As seis perguntas do slide 14 na busca vetorial pura.
- **Deve aparecer:**
  - a tabela com a posição do trecho certo em cada pergunta;
  - scores quase empatados entre "irmãos" (ATLAS, ÓRION e HÉLIOS; SKU 48213-B, C e D);
  - a resposta com citação.
- Antes de julgar a resposta, leia a linha "O trecho certo está entre eles?".

**02 — Híbrido.** Texto, vetor e híbrido (RRF) no mesmo índice.
- **Deve aparecer:**
  - os tokens do analisador (o hífen separa "48213-B" em `48213` e `b`);
  - a posição do trecho certo nas três consultas;
  - o score do híbrido perto de 0,03, que é o normal do RRF;
  - a resposta com o prazo do SKU 48213-B: 18 dias úteis.

**03 — Híbrido com reranking.** O semantic ranker sobre o top 50.
- **Deve aparecer:**
  - as notas do reranker, de 0 a 4;
  - o funil de 50 candidatos para 5 trechos;
  - a comparação de tokens entre 20 e 5 trechos no contexto.
- Um "—" no lugar da nota quer dizer que a etapa semântica não rodou: a consulta segue com a ordem do híbrido.
- Neste acervo pequeno, o híbrido pode já acertar. Nesse caso, a lição está na mudança de posição e no contexto menor.

**04 — Agêntico.** A pergunta composta: a aplicação planeja as subconsultas e o knowledge base as executa em paralelo.
- **Precisa de:** um deployment de chat com structured outputs e um AI Search numa região com agentic retrieval.
- **Cria:** o knowledge source `cap05-ks-acervo` e o knowledge base `cap05-kb-acervo`.
- Se o kernel já tinha importado o `azure-search-documents` 11.x, reinicie-o depois do `%pip`.
- **Deve aparecer:**
  - as subconsultas planejadas;
  - uma linha `searchIndex` por subconsulta na atividade;
  - a cobertura dos assuntos, que tende a chegar a 2/2;
  - a tabela de operações: 3 numa busca só contra 2N + 2 no agêntico.
- **Limpeza:** apaga o knowledge base e o knowledge source. Rode-a antes da limpeza do 00.

**05 — Grafo.** A pergunta multissalto: extração de entidades, grafo e a cadeia entre documentos.
- **Precisa de:** um deployment de chat com structured outputs.
- Na primeira vez, a Execução 2 faz 14 chamadas ao modelo, leva alguns minutos e grava o `grafo.json` na pasta. As execuções seguintes reaproveitam o arquivo.
- Rode uma vez antes da aula e apague o `grafo.json` só se quiser mostrar a extração ao vivo.
- **Deve aparecer:** o caminho Rolamentos Alfa → SKU 48213-B → Prensa P-400 → Projeto ATLAS e a resposta ligando os quatro fatos, com citação.
- Se a Execução 1 der erro do semantic ranker (cota ou região), continue da Execução 2. Antes da Execução 4, rode uma célula com `ids_top5 = []`.

### RAGless (slides 18 e 19)

Os quatro exercícios só usam o Azure OpenAI, são independentes e não criam recursos no Azure.

**01 — Contexto longo.** O acervo inteiro no prompt, com cache de prompt.
- Ajuste `JANELA_DO_MODELO` ao modelo do seu deployment.
- **Deve aparecer:** o acervo com cerca de 5 mil tokens e a tabela de cache. A 1ª chamada tende a vir com 0 tokens em cache, e as seguintes com a maior parte em cache, sem garantia.
- Se você ensaiou pouco antes da aula, a 1ª chamada pode já vir do cache.

**02 — Árvore de seções.** O sumário hierárquico da norma de segurança da informação; o modelo navega por ele.
- **Precisa de:** um deployment de chat com structured outputs.
- A primeira execução grava o `arvore.json`. Depois, cada pergunta faz duas chamadas ao modelo.
- **Deve aparecer:**
  - a árvore da norma e o sumário;
  - a seção aberta para cada pergunta (esperadas: 4.2, 6.1 e 7.2);
  - as respostas citando a seção.

**03 — Busca em arquivos.** Um agente que lista pastas, procura termos e lê arquivos de um pequeno repositório de código.
- Não edite a pasta `repositorio/`: as perguntas dependem dos números plantados nela.
- Rode uma vez antes da aula. Se a 2ª chamada de uma pergunta der erro 400, siga o passo 5 do README da pasta.
- **Deve aparecer:**
  - o rastro das ferramentas, passo a passo;
  - o timeout de produção: 8 s, em `config/producao.yaml` (o `gateway.py` só usa o padrão de 15 s se a chave faltar);
  - o que o runbook manda fazer no erro 504.

**04 — Respostas prontas.** Pares pergunta-resposta gerados e aprovados na ingestão; na consulta, um embedding e nenhum LLM.
- **Precisa de:** um deployment de chat com structured outputs e o deployment de embedding.
- A primeira execução grava o `respostas_aprovadas.json`, o arquivo de curadoria.
- **Deve aparecer:**
  - perguntas parecidas com as aprovadas recebendo a resposta pronta;
  - perguntas fora do escopo encaminhadas ao atendimento;
  - a mesma pergunta dando a mesma resposta três vezes.
- Para mostrar a curadoria, mude um `"aprovada"` para `false` no arquivo e rode de novo a partir da Execução 2.

### Bases vetoriais (slides 20 a 23)

Os seis seguem o mesmo roteiro: preparar os vetores, criar a estrutura vetorial, gravar, buscar e o RAG completo. São independentes entre si e de `tipos-de-rag`.

- **Deve aparecer, em todos:**
  - os 50 trechos gravados;
  - a busca por similaridade com o SKU 48213-B quase empatado com os irmãos, porque trocar a base não muda o vetor;
  - a resposta com citação.
- **Limpeza:** apaga o que o notebook criou. O serviço em si é apagado no portal.

| Exercício | Cria | Se der erro |
|---|---|---|
| `01-ai-search` | Índice `cap05-base-vetorial` (compara HNSW e busca exaustiva) | Use a chave de **administração** do AI Search. |
| `02-cosmos-db` | Banco `cap05` e contêiner `trechos` (índice `quantizedFlat`) | Erro ao criar o contêiner com a política vetorial: a causa provável é o "Vector Search for NoSQL API" ainda não estar ativo na conta. |
| `03-postgresql-pgvector` | Tabela `cap05_trechos` e índice HNSW | `no pg_hba.conf entry`: IP fora do firewall (uma regra nova leva até 5 minutos). Extensão recusada: libere `vector` em `azure.extensions`. |
| `04-azure-sql` | Tabela `dbo.cap05_trechos` | Erro 40613: o banco serverless estava pausado; rode a célula de conexão de novo. Driver não encontrado: ajuste o nome do driver na string. |
| `05-redis` | Índice `idx:cap05` e 50 hashes `cap05:trecho:*` | `unknown command 'FT._LIST'`: o cache foi criado sem o RediSearch. Chave recusada: ligue a Access Keys Authentication. |
| `06-documentdb` | Banco `cap05`, coleção `trechos` e índice `idx_vetor` (IVF) | Busca vazia logo depois de criar o índice: espere e rode a Execução 4 de novo. |

## Passo 4 — Depois da aula

1. Rode a limpeza do `tipos-de-rag/04-agentico` e depois a do `tipos-de-rag/00-indice-compartilhado`. Para isso, mude `APAGAR_RECURSOS` para `True` na última célula e execute só essa célula. Se o kernel foi reiniciado, execute antes a seção 0 (Preparação), que cria as conexões.
2. Nas bases vetoriais, rode a limpeza de cada notebook que usou.
3. Volte as flags para `False`. Senão, a próxima execução completa apaga tudo de novo no fim.
4. Apague o grupo de recursos no portal. O AI Search e as bases cobram enquanto existirem; apagar só os índices e as tabelas não para a cobrança.

## O acervo e o gabarito

- `acervo/` tem 14 documentos em Markdown: RH, financeiro, jurídico, segurança do trabalho, projetos, operações, compras e TI. É o "lake" do slide 24: a fonte da verdade, de onde todo índice se reconstrói.
- As armadilhas do slide 14 estão lá de propósito:
  - NR-12 rev. 3 e NR-10 rev. 3, com seções quase iguais;
  - os projetos ATLAS, ÓRION e HÉLIOS, escritos com o mesmo modelo de texto;
  - os SKUs 48213-B, C e D, com descrições quase idênticas;
  - "férias" x "descanso remunerado" e "encerrar contrato" x "cancelar assinatura".
- Para o grafo, há uma cadeia que nenhum trecho contém sozinho: a Rolamentos Alfa é fornecedora exclusiva do SKU 48213-B, que é usado na Prensa P-400, da qual depende o Projeto ATLAS. A suspensão da Rolamentos Alfa está em outro documento.
- `acervo/perguntas.json` é o gabarito: a pergunta, a categoria do slide e os trechos que a respondem. Os notebooks medem em que posição o trecho certo apareceu.

## Cuidados

- O `04-agentico` usa a versão GA do AI Search (API `2026-04-01`): a aplicação planeja as subconsultas e o knowledge base as executa. O planejamento feito pelo próprio serviço, como descrito no slide 17, existe por enquanto só na versão preview.
- As demos de cache de prompt do `ragless` seguem as regras dos modelos do GPT-4o até a família GPT-5.5, como o `gpt-5-mini`. Da família GPT-5.6 em diante, o cache funciona por pontos de corte e os números mudam.
- Editou o `.env` com o notebook aberto? Reinicie o kernel antes de rodar de novo: os notebooks leem o `.env` só na primeira vez.
- As chaves no `.env` simplificam a demonstração. Em produção, use Microsoft Entra ID e identidade gerenciada.
