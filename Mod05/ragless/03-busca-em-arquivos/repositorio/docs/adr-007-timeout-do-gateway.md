# ADR-007 — Timeout das chamadas ao gateway de pagamento

**Status:** aceita · **Data:** 12/05/2026 · **Decisores:** time de Pagamentos e time de Arquitetura

## Contexto

Até abril de 2026, produção usava o mesmo timeout de homologação, 30 s. No fechamento de março, o gateway do banco parceiro ficou lento, as chamadas passaram a esperar os 30 s inteiros e as 20 conexões do pool se esgotaram. O lote de pagamentos a fornecedores ficou parado por duas horas (incidente INC-2026-031).

Em produção, 99% das respostas do gateway chegam em até 2,4 s, e o contrato com o banco parceiro garante resposta em até 5 s.

## Decisão

- Timeout de 8 s por chamada em produção, na chave `timeout_segundos` de `config/producao.yaml`.
- Homologação continua com 30 s, porque o gateway de testes do banco parceiro é lento.
- O `TIMEOUT_PADRAO` de 15 s, em `src/pagamentos/gateway.py`, é só uma rede de segurança para quando a chave falta no arquivo do ambiente. Não é o valor de produção.

## Consequências

- 8 s cobre com folga os 5 s do contrato, sem segurar conexão por muito tempo.
- A chamada que passa de 8 s é abortada pelo serviço, e a ordem fica com status `FALHA_GATEWAY`, para reprocessamento. O timeout do nosso lado não entra nas retentativas, que valem só para os erros 502, 503 e 504 devolvidos pelo gateway.
- Qualquer valor acima de 10 s volta a arriscar o esgotamento do pool e precisa de aprovação do time de Arquitetura.
