# 00 — Índice compartilhado: a trilha de indexação

Notebook: `demo-indice-compartilhado.ipynb`

## O que mostra

A trilha de **indexação** do slide 9 (Ingestão → Extração → Chunking → Embedding → Indexação), passo a passo, sobre o acervo fictício da Contoso Industrial (`Cap05/acervo/`). No fim, o índice `cap05-acervo` do Azure AI Search fica pronto para os notebooks 01 a 05 de `tipos-de-rag`.

- **Slide 9:** as duas trilhas e o índice como contrato entre elas.
- **Slide 10:** quanto custa mudar depois cada decisão da indexação (quadro final do notebook).
- **Slides 11 e 12:** chunking por estrutura do documento (um trecho por seção `## `) comparado ao ponto de partida de 512 tokens com 25% de sobreposição.
- **Slide 23:** HNSW, a busca vetorial aproximada.

## Pré-requisitos no Azure

- **Azure OpenAI** com um deployment de embedding (`text-embedding-3-small` no `.env.example`). Use o endpoint no formato `https://<recurso>.openai.azure.com`: é ele que vai para o vetorizador do índice.
- **Azure AI Search**, de preferência no tier **Basic ou superior**, com a **chave de administração**, porque o notebook cria o índice. O semantic ranker do notebook 03 e o knowledge base do notebook 04 têm um plano gratuito, com cota mensal, em qualquer tier (no Free, só nas regiões que os oferecem nesse tier, como a Brazil South). O Basic dá mais índices e mais espaço, e só a partir dele existe o plano Standard, que libera o uso depois da cota.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT` (lida pela célula de configuração comum, mas não usada aqui), `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS`, `AZURE_SEARCH_ENDPOINT` e `AZURE_SEARCH_API_KEY`.

Copie `Cap05/.env.example` para `Cap05/.env` e preencha. O que faltar é perguntado na hora da execução. Não grave chaves no notebook.

## Como rodar

1. Instale as dependências com `pip install -r Cap05/requirements.txt` ou rode a célula `%pip` do notebook.
2. Abra o notebook nesta pasta e execute todas as células, em ordem.
3. Rodar de novo é seguro: o índice é atualizado e os trechos são regravados pelo mesmo `id`, sem duplicar.

## O que observar

- **Execução 1:** 50 trechos de 14 documentos, de ~30 a ~250 tokens cada, bem abaixo dos 512 tokens de referência.
- **Execução 2:** o modelo e a dimensão do embedding viram o contrato com a trilha de consulta.
- **Execução 3:** a tabela de campos que o serviço registrou: texto com `pt-BR.lucene`, filtros e o vetor com a dimensão do contrato.
- **Execução 4:** carga sem falhas e contagem do índice igual ao número de trechos.
- **Execução 5:** uma busca de texto por "reembolso" já devolve resultados.

## Limpeza

A última célula apaga o índice quando `APAGAR_RECURSOS = True`. **Os notebooks 01 a 05 dependem dele:** apague só no fim da aula. Se rodou o notebook 04, rode antes a limpeza dele, porque o knowledge base e o knowledge source apontam para este índice.

Mudou a dimensão do embedding no `.env`? Reinicie o kernel (o notebook lê o `.env` só uma vez), apague o índice e rode este notebook de novo, com `APAGAR_RECURSOS` de volta em `False`: a dimensão de um campo vetorial não muda depois de criada (é o "reindexar tudo" do slide 10). Mudou só o modelo, com a mesma dimensão? Nada falha: reinicie o kernel e rode o notebook inteiro, para regravar os 50 vetores com o modelo novo.
