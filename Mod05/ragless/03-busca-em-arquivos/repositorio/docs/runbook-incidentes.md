# Runbook de incidentes — servico-pagamentos

**Responsável:** time de Pagamentos · **Última revisão:** 14/08/2026

Use este runbook quando o alerta "Pagamentos — falhas no gateway" disparar. Cada seção trata um código HTTP devolvido pelo gateway do banco parceiro.

## Antes de qualquer ação

1. Abra o painel "Pagamentos — Gateway" e veja quais códigos de erro apareceram nos últimos 15 minutos.
2. Não reprocesse ordens à mão enquanto elas estiverem em retentativa: o reenvio por fora do serviço pode gerar pagamento em duplicidade.

## Erro 401 — credencial recusada

O gateway recusou o certificado de cliente do serviço. Não há retentativa automática para este erro.

1. Confira a validade do certificado no cofre de segredos: ele vence a cada 12 meses.
2. Se ele venceu, peça a renovação ao time de Segurança da Informação e reinicie o serviço depois da troca.

## Erro 422 — dados bancários inválidos

A ordem tem agência, conta ou CNPJ do fornecedor inválido. Não há retentativa automática para este erro.

1. Devolva a ordem para Contas a Pagar corrigir o cadastro do fornecedor.
2. Não altere dados bancários direto no banco de dados do serviço.

## Erro 502 ou 503 — gateway indisponível

O gateway está fora do ar ou em manutenção. O serviço já faz até 3 tentativas, com espera de 500 ms e depois de 1 s.

1. Se a página de status do gateway mostrar manutenção programada, pause o lote noturno e retome depois da janela.
2. Se não houver manutenção anunciada e o erro durar mais de 15 minutos, abra um incidente de severidade 2.

## Erro 504 — o gateway não respondeu a tempo

O gateway não recebeu a tempo a resposta do sistema do banco que fica atrás dele. O serviço já faz até 3 tentativas, com espera de 500 ms e depois de 1 s.

1. Verifique a página de status do gateway (https://status.gateway.example.com). Se o banco parceiro já declarou um incidente, acompanhe por lá e registre o número dele no nosso incidente.
2. Se mais de 5% das chamadas devolverem 504 por mais de 10 minutos, abra um incidente de severidade 2 no portal de incidentes e acione o plantão de Pagamentos.
3. Não aumente o timeout acima de 10 s sem aprovação do time de Arquitetura: timeout maior segura as conexões e já parou o lote de pagamentos (ver `docs/adr-007-timeout-do-gateway.md`).
4. Quando o gateway normalizar, reprocesse pelo próprio serviço só as ordens com status `FALHA_GATEWAY`.
