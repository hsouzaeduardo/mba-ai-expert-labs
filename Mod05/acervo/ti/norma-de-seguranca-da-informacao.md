# Norma de segurança da informação

**Código:** TI-NOR-01 · **Versão:** 5.1 · **Área:** Tecnologia da Informação · **Vigência:** 01/06/2026 · **Aprovação:** Comitê de Segurança da Informação

## 1. Objetivo e abrangência

### 1.1 Objetivo

Esta norma define as regras mínimas para proteger a confidencialidade, a integridade e a disponibilidade das informações da Contoso Industrial, em qualquer formato e em qualquer ambiente, seja na fábrica, no escritório, em trabalho remoto ou em serviços de nuvem.

### 1.2 A quem se aplica

Aplica-se a colaboradores, estagiários, aprendizes, prestadores de serviço e parceiros que acessem sistemas ou informações da empresa. O gestor de cada área responde pela aplicação da norma na sua equipe e pela comunicação de exceções ao Comitê de Segurança da Informação.

## 2. Classificação da informação

### 2.1 Pública

Informação liberada para divulgação externa, como comunicados de imprensa, catálogos comerciais e vagas abertas. Não exige proteção especial, mas só pode ser publicada por quem tem autorização da área de Comunicação.

### 2.2 Interna

Informação de uso geral dentro da empresa, como políticas, procedimentos e comunicados internos. Pode circular entre colaboradores, mas não deve ser enviada para fora da empresa sem necessidade de negócio.

### 2.3 Confidencial

Informação cujo vazamento causa prejuízo financeiro, jurídico ou de imagem, como orçamentos de projetos, propostas comerciais, dados pessoais de clientes e colaboradores e relatórios de auditoria. Só pode ser compartilhada com quem precisa dela para trabalhar e deve ser armazenada em repositórios com controle de acesso.

### 2.4 Restrita

Informação estratégica de acesso nominal, como planos de fusão e aquisição, segredos industriais, credenciais de sistemas e resultados financeiros antes da divulgação oficial. Exige criptografia em repouso e em trânsito, registro de quem acessou e aprovação do diretor responsável para qualquer compartilhamento.

## 3. Controle de acesso

### 3.1 Senhas

Senhas devem ter no mínimo catorze caracteres, não podem repetir nenhuma das dez últimas senhas usadas e não podem ser compartilhadas, nem mesmo com o suporte de TI. O uso do cofre de senhas corporativo é obrigatório para guardar senhas de sistemas.

### 3.2 Autenticação multifator

A autenticação multifator é obrigatória para o e-mail, para o acesso remoto à rede, para os sistemas financeiros e para qualquer conta com privilégio de administrador. O fator adicional deve ser o aplicativo autenticador corporativo; códigos por SMS não são aceitos.

### 3.3 Revisão periódica de acessos

A cada três meses, o gestor revisa os acessos da sua equipe aos sistemas críticos e confirma, no portal de Identidades, quais acessos continuam necessários. Acessos não confirmados em quinze dias são revogados automaticamente.

### 3.4 Desligamento e mudança de função

No desligamento de um colaborador, todos os acessos são revogados em até quatro horas após a comunicação do RH. Na mudança de função, os acessos da função anterior são removidos em até cinco dias úteis.

## 4. Uso aceitável de recursos

### 4.1 E-mail e mensageria

O e-mail corporativo é a ferramenta oficial para comunicação externa. É proibido configurar o encaminhamento automático de mensagens para contas pessoais e usar aplicativos de mensagem pessoais para enviar informação classificada como confidencial ou restrita.

### 4.2 Ferramentas de inteligência artificial generativa

Só podem ser usadas as ferramentas de inteligência artificial generativa aprovadas pela TI, como o assistente corporativo Contoso GPT, que roda no Azure OpenAI dentro do ambiente da empresa e não retém os dados enviados. É proibido colar informação classificada como confidencial ou restrita em ferramentas públicas de inteligência artificial, como chatbots gratuitos na internet. Todo conteúdo gerado por inteligência artificial deve ser revisado por uma pessoa antes de ser enviado a clientes ou usado em decisões, e o uso em processos críticos deve ser registrado no inventário de casos de uso de IA.

### 4.3 Dispositivos pessoais

Celulares e computadores pessoais só acessam e-mail e documentos da empresa por meio do aplicativo de gestão de dispositivos aprovado pela TI. É proibido baixar informação restrita em dispositivos pessoais.

## 5. Cópias de segurança e retenção

### 5.1 Frequência das cópias

Os sistemas críticos têm cópia de segurança incremental diária e cópia completa semanal, armazenadas em duas regiões de nuvem diferentes. A TI faz um teste de restauração a cada três meses e registra o resultado no relatório de continuidade.

### 5.2 Prazos de retenção

Registros contábeis e fiscais são mantidos por cinco anos, registros de acesso a sistemas por um ano e caixas de e-mail de ex-colaboradores por dois anos. Ao fim do prazo, a informação é eliminada de forma segura, salvo determinação jurídica em contrário.

## 6. Incidentes de segurança

### 6.1 Como reportar

Qualquer suspeita de incidente, como e-mail de phishing, perda de notebook, acesso indevido ou vazamento de dados, deve ser reportada imediatamente, e no máximo em duas horas após a descoberta, pelo portal Segurança ou pelo ramal 4040. Não tente investigar sozinho nem apagar evidências.

### 6.2 Classificação de severidade

O time de resposta classifica o incidente em baixa, média, alta ou crítica severidade, conforme o impacto e a quantidade de dados envolvidos. Incidentes de severidade crítica acionam o comitê de crise em até uma hora.

### 6.3 Comunicação à autoridade e aos titulares

Quando o incidente envolve dados pessoais com risco relevante aos titulares, o encarregado de dados avalia o caso e comunica a Autoridade Nacional de Proteção de Dados e os titulares afetados em até três dias úteis, conforme a regulamentação vigente.

## 7. Serviços de nuvem e fornecedores de TI

### 7.1 Avaliação de risco antes da adoção

Nenhum serviço de nuvem ou fornecedor de TI pode tratar informação confidencial ou restrita sem uma avaliação de risco de segurança aprovada pela TI, que verifica certificações, controles de acesso, criptografia e plano de continuidade do fornecedor.

### 7.2 Localização e transferência dos dados

Dados pessoais de clientes e colaboradores devem ser armazenados em regiões de nuvem localizadas no Brasil. A transferência para outro país só é permitida com aprovação do encarregado de dados e com as cláusulas padrão de proteção de dados previstas na regulamentação.

## 8. Sanções e exceções

### 8.1 Sanções

O descumprimento desta norma sujeita o colaborador a medidas disciplinares, que vão da advertência à demissão por justa causa, sem prejuízo das medidas legais cabíveis.

### 8.2 Exceções

Exceções a esta norma precisam de justificativa de negócio, avaliação de risco e aprovação do diretor de segurança da informação, com validade máxima de seis meses e registro no inventário de exceções.
