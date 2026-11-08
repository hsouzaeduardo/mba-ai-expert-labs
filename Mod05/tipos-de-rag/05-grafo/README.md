# 05 — RAG em grafo: ligar fatos de documentos diferentes

Notebook: `demo-grafo.ipynb`

## O que mostra

O **degrau 4** do slide 17 ("Falha em pergunta que exige ligar fatos de documentos diferentes" → Grafo) e a linha **Grafo** do slide 15: percorrer entidades e relações do acervo, com indexação cara e GraphRAG fora do AI Search. Também ilustra a regra do slide 13: só se sobe para o grafo por sintoma medido.

A pergunta é a `multissalto` do gabarito (`acervo/perguntas.json`): *"A suspensão da Rolamentos Alfa coloca algum projeto da empresa em risco?"*. A resposta depende de quatro documentos (fornecedores homologados → plano de manutenção da Prensa P-400 → projeto ATLAS → comunicado de suspensão), e nenhum trecho a contém sozinho.

1. **O limite do híbrido com reranking:** a busca híbrida com semantic ranker (top 5) cobre só parte da cadeia; o elo da P-400 tende a ficar de fora.
2. **Indexação do grafo (a parte cara):** uma chamada `responses.parse` por documento (14 no total), com structured outputs, extrai triplas (origem, relação, destino) com o trecho de origem; uma normalização ingênua junta os nomes, e o grafo vira um `networkx.MultiDiGraph`.
3. **Consulta no grafo:** das entidades citadas na pergunta até os projetos, pelo caminho mais curto, com o desenho do subgrafo.
4. **Resposta com o grafo:** as relações do caminho e os trechos de origem viram o contexto do mesmo `responder`, com citação.

## Pré-requisitos no Azure

- O índice `cap05-acervo`, criado pelo notebook `../00-indice-compartilhado` (usado só na Execução 1). Se ele não existir, a célula do AI Search para com uma mensagem clara.
- **Azure AI Search:** o mesmo serviço do notebook 00 (tier Basic ou superior), numa região com semantic ranker. A Execução 1 faz uma consulta semântica por execução do notebook. O semantic ranker começa no plano gratuito, com uma cota mensal de consultas; esgotada a cota, a consulta devolve erro de cobrança até o serviço passar para o plano Standard, pago por uso (no portal: **Settings > Premium features**).
- **Azure OpenAI:** o mesmo deployment de embedding do notebook 00 e um deployment de chat que aceite structured outputs, como o `gpt-5-mini`.
- Nenhum recurso novo no Azure: o grafo fica em memória (`networkx`) e no arquivo `grafo.json`.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS` (os mesmos valores do notebook 00), `AZURE_SEARCH_ENDPOINT` e `AZURE_SEARCH_API_KEY`.

Os valores vêm de `Cap05/.env`, uma cópia preenchida do `.env.example`. O que faltar é perguntado na hora da execução.

## Como rodar

1. Rode antes o notebook 00. Uma vez basta: o índice fica no serviço.
2. Abra este notebook e execute todas as células, em ordem.
3. Se a Execução 1 der erro do semantic ranker (cota mensal do plano gratuito esgotada, região sem o recurso), continue a partir da Execução 2 e, antes da Execução 4, rode uma célula com `ids_top5 = []`: a comparação da Execução 4 vai mostrar 0/4 para a Execução 1.
4. Na primeira vez, a Execução 2 faz 14 chamadas ao modelo de chat e pode levar alguns minutos. O resultado fica em `grafo.json`, nesta pasta, e as execuções seguintes leem o arquivo sem chamar o modelo. **Para a aula:** rode o notebook uma vez antes e apague `grafo.json` só se quiser mostrar a extração ao vivo.

## O que observar

- **Execução 1:** a linha "Elos da cadeia no top 5" (tende a ficar abaixo de 4/4) e a resposta, que deve se abster ou responder só em parte.
- **Execução 2:** as colunas de tokens (os de saída incluem o raciocínio do modelo) e a tabela de entidades: primeiro os nomes diferentes que viraram um nó só, depois os nós mais conectados.
- **Execução 3:** o caminho Rolamentos Alfa → SKU 48213-B → Prensa P-400 → Projeto ATLAS, em 3 saltos. Outros projetos podem aparecer com caminhos mais longos, passando por nós genéricos. Em caso de empate, só um caminho segue para a Execução 4: confira se ele passa pelo SKU e pela prensa.
- **Execução 4:** "Elos da cadeia no contexto" contra a Execução 1, com o mesmo `responder`. A resposta deve ligar os quatro fatos, citando cada trecho.
- A extração é feita por um modelo: nomes dos nós, número de relações e até a existência do caminho podem mudar quando o `grafo.json` é refeito. Se não aparecer caminho, a Execução 3 mostra o motivo, que quase sempre está nos nomes: o mesmo item com dois nomes ("P-400" e "Prensa P-400") ou o projeto escrito só como "ATLAS". As relações descartadas aparecem na saída da Execução 2, com exemplos.

## Limpeza

Nada a apagar no Azure: este notebook não cria recursos. O único arquivo gerado é o `grafo.json`, nesta pasta: apague-o para reextrair o grafo ou para deixar a pasta como veio. O índice é apagado pela célula de limpeza do notebook 00.
