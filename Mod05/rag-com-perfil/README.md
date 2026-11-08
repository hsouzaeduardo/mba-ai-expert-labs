# RAG com perfil — a mesma base, duas respostas

Notebook: `demo-rag-com-perfil.ipynb`

## O que mostra

O fluxo do slide 26 ("Como a permissão do usuário chega até o documento recuperado"): dois usuários consultam o **mesmo índice** do Azure AI Search, e cada um só recupera o que o seu perfil permite. É a "Permissão por usuário" do slide 5, a linha "Respeitar a permissão de quem perguntou" do slide 6, o anti-padrão 04 do slide 28 e a frase do slide 25.

- **Os documentos:** a política de descanso remunerado (`acervo/rh/`), que a empresa toda pode ver, e o Projeto ATLAS (`acervo/projetos/`), restrito à equipe do projeto.
- **Os usuários:** Mariana Costa, gerente do Projeto ATLAS, vê os dois documentos; Rafael Souza, analista de Logística, só a política de descanso. Os grupos de cada um ficam num dicionário que simula o que o Microsoft Entra ID devolveria no login.

1. **O cenário:** os dois documentos, os dois usuários e a matriz de quem vê o quê. Cada trecho herda a lista de grupos do seu documento.
2. **No índice:** o campo `group_ids`, filtrável e não recuperável (`hidden=True` no SDK), e a prova de que ele nunca volta no resultado.
3. **A aplicação monta o filtro e o AI Search filtra na busca:** `group_ids/any(g: search.in(g, '...'))` na busca híbrida, com `preFilter`. A mesma pergunta sobre o ATLAS traz trechos dele para Mariana e nenhum para Rafael.
4. **Geração segura:** a mesma pergunta, duas respostas. Uma pergunta que os dois podem responder, uma que só Mariana pode, e um pedido "com jeitinho" de Rafael para o modelo ignorar as restrições.
5. **O anti-padrão:** buscar sem filtro e descartar depois, em Python. A tela é a mesma, mas o orçamento do ATLAS já trafegou até a aplicação.
6. **Na manutenção:** a permissão muda com um `merge_documents` só no campo `group_ids`, sem embedding e sem reindexar. A segunda célula desfaz a mudança.
7. **O ponto crítico:** com um grupo forjado na lista, o filtro deixa o ATLAS passar. Os grupos têm de vir do token validado no servidor, nunca da requisição.

## Pré-requisitos no Azure

- **Azure OpenAI** com um deployment de chat (por exemplo, `gpt-5-mini`) e um deployment de `text-embedding-3-small`.
- **Azure AI Search** em qualquer tier, com a chave de **administração** no `.env`: o notebook cria o índice `cap05-rag-com-perfil`. No Free, o limite é de 3 índices por serviço.
- Não depende de nenhum outro notebook: o índice é próprio, com os 7 trechos dos 2 documentos.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS`, `AZURE_SEARCH_ENDPOINT` e `AZURE_SEARCH_API_KEY`.

Os valores vêm de `Cap05/.env`, uma cópia preenchida do `.env.example`. O que faltar é perguntado na hora da execução.

## Como rodar

1. Abra o notebook, escolha o kernel do `.venv` e execute todas as células, em ordem.
2. Rodar de novo é seguro: a carga regrava os mesmos 7 trechos, com as permissões originais.

## O que observar

- **Execução 1:** 7 trechos, 4 da política de descanso e 3 do ATLAS. Nenhuma linha de código diz "Rafael não pode ver o ATLAS": a permissão sai do cruzamento entre os grupos do usuário e os do documento.
- **Execução 2:** na tabela de campos, o `group_ids` é o único filtrável e não recuperável. A busca sem `select` devolve até o vetor, mas não o `group_ids`.
- **Execução 3:** o filtro de cada usuário aparece por extenso. Para Rafael, os 3 trechos vêm da política de descanso: o ATLAS nem entra no ranking.
- **Execução 4:** Mariana recebe o orçamento do ATLAS (R$ 4,2 milhões, dos quais R$ 1,6 milhão já executado), com citação; Rafael recebe "Não há evidência suficiente nos trechos recuperados.". O pedido "com jeitinho" não muda nada, porque o número nunca entrou no contexto.
- **Execução 5:** a tabela "filtro na busca x filtro depois de recuperar" e o texto do ATLAS que chegou à aplicação num pedido de Rafael.
- **Execução 6:** o `merge_documents` manda só `id` e `group_ids`. Rafael passa a ver o ATLAS em poucos segundos e, depois da segunda célula, deixa de ver.
- **Execução 7:** o filtro forjado é idêntico ao de Mariana. O AI Search compara strings e não sabe quem perguntou.
- As respostas do modelo variam de uma execução para outra. O que não varia é o filtro: sem `grp-projeto-atlas`, nenhum trecho do ATLAS volta da busca.

## Se der erro

| Sintoma | Causa provável |
|---|---|
| 403 ao criar o índice | A chave do `.env` é de consulta. Use a chave de **administração** do AI Search. |
| Erro de cota ao criar o índice | O serviço Free já tem 3 índices. Apague um que não use ou use outro serviço. |
| Rafael continua vendo o ATLAS | A Execução 6 parou antes da segunda célula. Rode o notebook de novo desde o início: a carga da Execução 2 regrava as permissões originais. |

## Limpeza

A última célula apaga o índice `cap05-rag-com-perfil` e vem desligada (`APAGAR_RECURSOS = False`). Para apagar, mude para `True` e execute só essa célula; se o kernel foi reiniciado, execute antes a seção 0 (Preparação). Nenhum outro notebook depende deste índice.
