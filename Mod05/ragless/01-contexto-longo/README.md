# 01 — Contexto longo: o acervo inteiro no prompt

Notebook: `demo-contexto-longo.ipynb`

## O que mostra

A primeira linha RAGless dos slides 18 e 19, **sem busca e sem índice**: o acervo fictício da Contoso Industrial (`Cap05/acervo/`, 14 documentos) vai inteiro no prompt, e o cache de prompt do Azure OpenAI evita pagar a leitura cheia de novo a cada chamada. O slide diz quando isso cabe: acervo pequeno e estável, que cabe na janela do modelo.

1. **O acervo cabe na janela?** O acervo inteiro tem ~5 mil tokens (`o200k_base`), uns 4% de uma janela de 128 mil.
2. **Perguntar sem busca:** três perguntas do gabarito (código de norma, string exata e multissalto), com instruções e acervo como prefixo estável e a pergunta no fim. O notebook conta quantos dos arquivos esperados a resposta citou.
3. **O cache em ação:** tokens de entrada, tokens em cache e latência de cada chamada, com a 1ª pergunta repetida no fim.
4. **Custo por pergunta x RAG:** o acervo inteiro contra 5 trechos típicos (~9 vezes mais tokens de entrada por pergunta) e a projeção mensal em tokens.

## Pré-requisitos no Azure

- **Azure OpenAI** com um deployment de chat de um modelo do GPT-4o até a família GPT-5.5, por exemplo o `gpt-5-mini` sugerido no `.env.example`. A Execução 3 mostra o cache de prompt desses modelos. Da família GPT-5.6 em diante, o cache só é lido nos pontos de corte (*breakpoints*) e, neste notebook, perguntas diferentes não reaproveitam o acervo.
- Não usa Azure AI Search, embedding nem índice. Não depende do notebook `tipos-de-rag/00-indice-compartilhado`.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` e `AZURE_OPENAI_DEPLOYMENT`. As variáveis de embedding e do AI Search não são lidas.

Os valores vêm de `Cap05/.env`, uma cópia preenchida do `.env.example`. O que faltar é perguntado na hora da execução. Não grave chaves no notebook.

## Como rodar

1. Instale as dependências com `pip install -r Cap05/requirements.txt` ou rode a célula `%pip` do notebook.
2. Abra o notebook nesta pasta e execute todas as células, em ordem.
3. Se ensaiou pouco antes da aula, a 1ª chamada pode já vir do cache. O cache em memória costuma ser apagado depois de 5 a 10 minutos sem uso, e sempre em até uma hora. Só no `gpt-5.5`, que já vem com a retenção estendida ligada, o cache pode durar até 24 horas; nos outros modelos, o notebook usa o padrão em memória.

## O que observar

- **Execução 1:** `JANELA_DO_MODELO = 128_000` é uma referência (a entrada do `gpt-4o`); ajuste ao modelo do deployment. O `gpt-5-mini` aceita 272 mil tokens de entrada.
- **Execução 2:** sem busca não há erro de recuperação, e até a multissalto tende a sair. Em compensação, a citação é só por arquivo e todo usuário recebe o acervo inteiro.
- **Execução 3:** a 1ª chamada tende a vir com 0 tokens em cache, porque é ela que grava o prefixo; da 2ª em diante, a maior parte da entrada tende a vir do cache. O acerto não é garantido: se tudo vier zerado, rode a célula de novo; se continuar zerado, o modelo pode não ter cache de prompt. Se só a pergunta repetida acertar, o deployment provavelmente é da família GPT-5.6 em diante (veja os pré-requisitos).
- **Execução 4:** o cache baixa o preço da leitura, não a quantidade lida. O custo migra para a consulta: com acervo grande, volátil ou com permissão por usuário, o índice volta a valer.
- As respostas mudam a cada execução; os tokens do acervo, não.

## Limpeza

Nada a apagar: este notebook não cria recursos no Azure.
