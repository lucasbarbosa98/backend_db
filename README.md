# backend_db
# db_backend

1.- Tomando como base a estrutura do banco de dados fornecida (conforme diagrama [ER_diagram.png] e/ou script DDL [1_create_database_ddl.sql], disponibilizados no repositório do github): Construa uma consulta SQL que retorne o nome, e-mail, a descrição do papel e as descrições das permissões/claims que um usuário possui.

R:
"""Selecionar todas as tabelas que deverão ser feitas as consultas"""
 SELECT
  u.name               AS nome,
  u.email              AS email,
  r.description        AS papel,

"""Agrupa todas as permissões vinculadas ao usuário, separando cada uma delas por "," """
  GROUP_CONCAT(
    c.description
    SEPARATOR ', '
  )                    AS permissoes

"""Busca quais usuários possuem o mesmo ID salvo na tabela roles"""
FROM users u
LEFT JOIN roles r
  ON u.role_id = r.id

"""Retorna todas as permissões associadas ao usuário, linkando o ID as claims"""
LEFT JOIN user_claims uc
  ON u.id = uc.user_id
LEFT JOIN claims c
  ON uc.claim_id = c.id

"""Agrupa o retorno dos resultados pelo ID do usuário, ordenando o retorno por nome de usuário e permissões"
GROUP BY
  u.id
ORDER BY
  u.name;



2.- Utilizando a mesma estrutura do banco de dados da questão anterior, rescreva a consulta anterior utilizando um ORM (Object Relational Mapping) de sua preferência utilizando a query language padrão do ORM adotado (ex.: Spring JOOQ, EEF LINQ, SQL Alchemy Expression Language, etc).
R: rota: 
@router.get("/users")
def get_users_with_roles_and_permissions():


3.- Utilizando a mesma estrutura do banco de dados fornecida anteriormente, e a linguagem que desejar, construa uma API REST que irá listar o papel de um usuário pelo “Id” (role_id).
R: rota:
@router.get("/users/{role_id}")
def get_users_by_role(role_id: int): 



4.- Utilizando a mesma estrutura do banco de dados fornecida anteriormente, e a linguagem que desejar, construa uma API REST que irá criar um usuário. Os campos obrigatórios serão nome, e-mail e papel do usuário. A senha será um campo opcional, caso o usuário não informe uma senha o serviço da API deverá gerar essa senha automaticamente.
r: rota: 
@router.post("/create/user")
def create_user(user: dict):


5.- Crie uma documentação que explique como executar seu projeto em ambiente local e também como deverá ser realizado o ‘deploy’ em ambiente produtivo.
R: Centralizei a execução no módulo app.py, ao executar um dos comandos: uvicorn backend.app:app --reload | uvicorn app:app --host 127.0.0.1 --port 8000, exemplifiquei cada uma das resuisições aceitas pelo serviço também.
Para ambiente produtivo, busquei adequar o serviço para que possa ser criada uma imagem Docker e após as configurações, poderá ser realizado o deploy da aplicação.


6.- Nossos analistas de qualidade reportaram uma falha que só acontece em ambientes diferentes do local/desenvolvimento, os engenheiros responsáveis pelo ambiente de Homologação já descartaram problemas de infra-estrutura, temos que levantar o que está acontecendo.

Ao executar o comando para listar os logs (no stdio) do Pod de Jobs, capturei o seguinte registro de log:

[2020-07-06 20:24:49,781: INFO/ForkPoolWorker-2] [expire_orders] - Finishing job…

[2020-07-06 20:34:49,721: INFO/ForkPoolWorker-1] [renew_wallet_x_access_tokens] Starting task that renew Access Tokens from Wallet X about to expire

[2020-07-06 20:34:49,723: ERROR/ForkPoolWorker-1] Task tasks.wallet_oauth.renew_wallet_x_access_tokens[ee561a2e-e837-4d98-b771-07f4e2b5ec70] raised unexpected: AttributeError("module 'core.settings' has no attribute ‘WALLET_X_TOKEN_MAX_AGE'") Traceback (most recent call last): File "/usr/local/lib/python3.7/site-packages/celery/app/trace.py", line 385, in trace_task R = retval = fun(args, kwargs) File "/usr/local/lib/python3.7/site-packages/celery/app/trace.py", line 650, in protected_call return self.run(args, kwargs) File "/opt/worker/src/tasks/wallet_oauth.py", line 15, in renew_wallet_x_access_tokens expire_at = now - settings.WALLET_X_TOKEN_MAX_AGE AttributeError: module 'core.settings' has no attribute ‘WALLET_X_TOKEN_MAX_AGE'

[2020-07-06 20:34:49,799: INFO/ForkPoolWorker-2] [expire_orders] - Starting job…

[2020-07-66 20:34:49,801: INFO/ForkPoolWorker-2] [expire_orders] - Filtering pending operations older than 10 minutes ago.

De acordo com o log capturado, o que pode estar originando a falha?
R: Ausência de validação ou valor do token: WALLET_X_TOKEN_MAX_AGE, possívelmente no módulo core.settings.


7.- Ajude-nos fazendo o ‘Code Review’ do código de um robô/rotina que exporta os dados da tabela “users” de tempos em tempos. O código foi disponibilizado no mesmo repositório do git hub dentro da pasta “bot”. ATENÇÃO: Não é necessário implementar as revisões, basta apenas anota-las em um arquivo texto ou em forma de comentários no código.
R: Comentários no código


8.- Qual ou quais Padrões de Projeto/Design Patterns você utilizaria para normalizar serviços de terceiros (tornar múltiplas interfaces de diferentes fornecedores uniforme), por exemplo serviços de disparos de e-mails, ou então disparos de SMS. ATENÇÃO: Não é necessário implementar o Design Pattern, basta descrever qual você utilizaria e por quais motivos optou pelo mesmo.
R: Injeção de dependências permite fácil manutenção e ajustes quando necessário, pois as classes são isoladas e bem definidas. Isso facilita a substituição de serviços ou alterações de comportamento, sem impactar o restante do sistema.

Serviço centraliza a lógica de negócio em um único módulo, facilitando sua reutilização em diferentes partes da aplicação. Além disso, mantém essa lógica isolada, o que torna ajustes e manutenções muito mais simples e seguros.

Optei por esses dois padrões por serem os que mais estou habituado a utilizar no dia a dia, acredito que, conforme o caso envolva múltiplas interfaces e diferentes situações de uso, padrões que isolam suas responsabilidades serão mais adequados para a escalabilidade do sistema. Dessa forma, é possível aplicar outras lógicas e regras isoladas conforme o contexto de uso, evitando códigos duplicados, assim como classes e arquivos extensos que podem causar problemas para a implementação de novas funcionalidades, dificultar a manutenção, leitura e entendimento do código.