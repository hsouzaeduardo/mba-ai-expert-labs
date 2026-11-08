# servico-pagamentos

Serviço da Contoso Industrial que envia as ordens de pagamento a fornecedores para o gateway do banco parceiro, em lotes noturnos.

## Estrutura

- `src/pagamentos/gateway.py`: cliente do gateway, que envia cada ordem e devolve o status final dela.
- `src/pagamentos/retentativas.py`: política de retentativas para os erros temporários do gateway.
- `config/`: um arquivo por ambiente, `producao.yaml` e `homologacao.yaml`.
- `docs/runbook-incidentes.md`: o que fazer quando o gateway devolve erro.
- `docs/adr-007-timeout-do-gateway.md`: por que o timeout de produção tem o valor que tem.

## Configuração

O serviço lê o arquivo do ambiente indicado na variável `PAGAMENTOS_AMBIENTE` (`producao` ou `homologacao`). URL, timeout e pool de conexões do gateway ficam nesse arquivo, e não no código.

Antes de mudar qualquer valor de produção, leia o runbook e as decisões de arquitetura (ADRs) da pasta `docs/`.

---

Repositório fictício, criado para a aula de Arquitetura de RAG no Azure (Cap. 5).
