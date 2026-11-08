# 04 — RAG agêntico: uma pergunta, várias buscas

Notebook: `demo-agentico.ipynb`

## O que mostra

O **degrau 3** do slide 17 (falha em pergunta que junta dois assuntos ou exige mais de uma fonte → agentic retrieval planeja subconsultas) e a linha **Agêntico** do slide 15. A pergunta é a `pergunta-composta` do gabarito (`acervo/perguntas.json`): o teto da diária de hotel em Joinville e o que a NR-12 rev. 3 exige antes de abrir a proteção da prensa.

1. **Uma busca só:** consulta híbrida com semantic ranker (como no notebook 03), top 5, e a cobertura dos dois assuntos (por exemplo, `1/2`).
2. **Planejamento:** o Azure OpenAI divide a pergunta em 2 a 4 subconsultas, com saída estruturada (`responses.parse` e um modelo Pydantic).
3. **Agentic retrieval:** o knowledge source `cap05-ks-acervo` e o knowledge base `cap05-kb-acervo` executam as subconsultas em paralelo, com semantic ranker, e juntam os resultados. O notebook mostra a atividade, as referências e a cobertura.
4. **Resposta com citação** e a conta das operações de cada caminho ("Várias chamadas", slide 15).

**GA x preview.** Na API GA `2026-04-01` (SDK `azure-search-documents` 12.0.0), o knowledge base só executa: o app planeja e manda as subconsultas como *intents*. O planejamento pelo próprio knowledge base, a partir da conversa, e a síntese da resposta existem só nas versões preview da API (hoje, a `2026-08-01-preview`), sem SLA. É esse o modo que o slide 17 descreve.

## Pré-requisitos no Azure

- O índice `cap05-acervo`, criado pelo notebook `../00-indice-compartilhado`, com o vetorizador `vetorizador-aoai`: o knowledge base usa esse vetorizador para vetorizar cada subconsulta.
- **Azure AI Search** numa região com agentic retrieval e semantic ranker (Brazil South tem), com a **chave de administração**: o notebook cria o knowledge source e o knowledge base.
- **Cobrança:** o agentic retrieval é cobrado por token. O plano Free, que é o padrão, dá uma cota mensal; esgotada a cota, o retrieve devolve erro de pagamento até o plano Standard ser ativado em **Settings > Premium features > Knowledge retrieval** (tier Basic ou superior). Desde a API `2026-04-01`, essa opção é separada da do semantic ranker.
- **Azure OpenAI** com o deployment de chat (planejamento e resposta), que precisa aceitar **structured outputs**, como o `gpt-5-mini`, e o mesmo deployment de embedding do notebook 00.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS` (os mesmos valores do notebook 00), `AZURE_SEARCH_ENDPOINT` e `AZURE_SEARCH_API_KEY`.

Os valores vêm de `Cap05/.env`, uma cópia preenchida do `.env.example`. O que faltar é perguntado na hora da execução.

## Como rodar

1. Rode antes o notebook 00. Uma vez basta: o índice fica no serviço.
2. Rode a célula `%pip`. Se o kernel já tinha importado uma versão antiga do `azure-search-documents` (a 11.x, por exemplo), reinicie o kernel antes de seguir.
3. Execute as células em ordem. Rodar de novo é seguro: o knowledge source e o knowledge base são atualizados, não duplicados.

## O que observar

- **Execução 1:** a coluna "assunto da pergunta" e a cobertura do top 5. Os trechos de prensa e de NR-12 tendem a ocupar as cinco vagas. Se der `2/2`, anote a nota do reranker do trecho do teto da diária, para comparar com a da Execução 3.
- **Execução 2:** subconsultas curtas, uma por assunto, com "NR-12 rev. 3" e "P-400" intactos.
- **Execução 3:** uma linha `searchIndex` por subconsulta na atividade, a coluna "atividade de origem" nas referências e a cobertura, que tende a `2/2`. O retrieve pede o corte de 2,5 na nota do reranker (`reranker_threshold`): confira na coluna "nota do reranker" se alguma referência ficou abaixo, porque a documentação não deixa claro se o corte vale para as referências ou só para o texto extraído. Se uma linha da atividade mostrar erro, confira o vetorizador do índice: rodar o notebook 00 de novo o regrava com a chave atual.
- **Execução 4:** cada parte da resposta citando o trecho do seu assunto, e a tabela de operações: 3 no pipeline de uma busca, 2N + 2 no agêntico (N subconsultas).
- Os resultados variam a cada execução (o plano muda). Por isso o notebook mostra notas e cobertura, e não fixa um ranking.

## Limpeza

Com `APAGAR_RECURSOS = True`, a última célula apaga primeiro o knowledge base e depois o knowledge source: o serviço recusa apagar um knowledge source em uso. O índice continua; quem o apaga é a limpeza do notebook 00, que deve rodar depois desta.
