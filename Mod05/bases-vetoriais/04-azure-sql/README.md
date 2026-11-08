# 04 — Onde o vetor mora: Azure SQL Database

Notebook: `demo-azure-sql.ipynb`

## O que mostra

Os vetores do acervo fictício da Contoso Industrial (`Cap05/acervo/`) guardados no **Azure SQL Database**, com o tipo nativo `VECTOR` e a busca exata com `VECTOR_DISTANCE`. O roteiro é o mesmo dos outros cinco notebooks de `bases-vetoriais`: preparar os vetores → criar a estrutura vetorial → gravar → buscar → RAG completo.

- **Slides 20 e 21:** a pergunta que decide onde o vetor mora (o dado muda em tempo real?) e a resposta mais comum: usar o que a empresa já opera.
- **Slide 22:** a linha do Azure SQL. Até 1.998 dimensões, DiskANN, sem reranking; "já é a base da casa e a dimensão cabe".
- **Slide 23:** o DiskANN no triângulo recall, memória e tempo de indexação, e como ele lida com dado que muda. O notebook usa a busca exata e só comenta o índice, que exige pelo menos 100 linhas com vetor (o acervo tem 50 trechos).

## Pré-requisitos no Azure

- **Azure SQL Database.** O free tier basta: um General Purpose serverless, com até 10 bancos gratuitos por assinatura e, por banco, 100 mil vCore-segundos, 32 GB de dados e 32 GB de backup por mês. O tipo `VECTOR` é GA e não exige feature flag.
- **Firewall** do servidor lógico liberando o IP público da máquina da aula.
- Um login com permissão para criar tabela (para a aula, o administrador do servidor serve).
- **ODBC Driver 17 ou 18 for SQL Server** instalado na máquina. Para conferir: `python -c "import pyodbc; print(pyodbc.drivers())"`.
- **Azure OpenAI**, com um deployment de embedding (`text-embedding-3-small`) e um de chat.

## Variáveis de ambiente

`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_MODEL`, `AZURE_OPENAI_EMBEDDING_DIMENSIONS` (aqui, no máximo 1.998) e `AZURE_SQL_CONNECTION_STRING`.

Os valores vêm de `Cap05/.env`, uma cópia preenchida do `.env.example`. Sobre a `AZURE_SQL_CONNECTION_STRING`:

- O `.env.example` vem com `Driver={ODBC Driver 18 for SQL Server}`. Se a máquina só tiver o 17, troque o nome; a célula de conexão avisa e lista os drivers instalados.
- Mantenha `Encrypt=yes;TrustServerCertificate=no`: no Driver 17 o padrão de `Encrypt` é `no`; no 18, `yes`.
- Senha com `;` ou `=`: coloque-a entre chaves, `Pwd={...}`. Evite `{` e `}` na senha: dentro das chaves, um `}` sozinho encerra o valor. Evite também `${`, porque o python-dotenv troca `${NOME}` pelo valor da variável de ambiente, mesmo entre aspas.
- Usuário e senha na string simplificam a aula. Em produção, use Microsoft Entra ID (keyword `Authentication` do driver, por exemplo com identidade gerenciada).

## Como rodar

1. Instale as dependências com `pip install -r Cap05/requirements.txt` ou rode a célula `%pip` do notebook.
2. Abra o notebook nesta pasta e execute todas as células, em ordem. Ele não depende dos notebooks de `tipos-de-rag`.
3. Banco serverless pausado: a primeira conexão pode falhar com o erro 40613 enquanto ele retoma (em geral, menos de um minuto). Rode a célula de conexão de novo. Se continuar falhando no free tier, veja no portal se o limite gratuito do mês acabou: com a opção de pausar ao atingir o limite, o banco fica inacessível até o início do mês seguinte.
4. Rodar de novo é seguro: o `MERGE` regrava as mesmas linhas pelo `id` do trecho, sem duplicar.

## O que observar

- **Execução 2:** o vetor é só mais uma coluna, `VECTOR(1536)`, e o `sys.columns` mostra a dimensão gravada no tipo.
- **Execução 3:** 50 linhas na tabela, também na segunda execução. O vetor viaja como texto JSON e passa por `NVARCHAR(MAX)` antes de virar `VECTOR`, porque o driver ODBC envia texto longo como `ntext`.
- **Execução 4:** busca exata, sem índice e sem aproximação, e mesmo assim os SKUs 48213-B, C e D tendem a quase empatar. Trocar a base não corrige a recuperação.
- **Execução 5:** a resposta cita os `id` dos trechos que vieram do banco.

## Limpeza

A última célula apaga a tabela `dbo.cap05_trechos` quando `APAGAR_RECURSOS = True` e, em qualquer caso, fecha a conexão: uma conexão aberta impede a pausa automática do banco serverless e consome vCore-segundos. O servidor e o banco não são criados pelo notebook; apague-os no portal quando não forem mais necessários.

## Referências

- Microsoft Learn: [tipo `vector`](https://learn.microsoft.com/sql/t-sql/data-types/vector-data-type), [keywords da string ODBC, entre elas `Encrypt`](https://learn.microsoft.com/sql/connect/odbc/dsn-connection-string-attribute), [free tier do Azure SQL Database](https://learn.microsoft.com/azure/azure-sql/database/free-tier), [pausa automática do serverless e erro 40613](https://learn.microsoft.com/azure/azure-sql/database/serverless-tier-auto-pause-resume) e [chaves na string ODBC](https://learn.microsoft.com/sql/odbc/reference/syntax/sqldriverconnect-function).
