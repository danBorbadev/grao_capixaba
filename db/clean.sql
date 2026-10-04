-- Verificando como está a estrutura da tabela de clientes;
select column_name, data_type from information_schema.columns
where table_schema = 'public' and table_name='clientes';

-- Panorama geral dos clientes;
select count(*)
from clientes; -- 2141 Clientes capturados na plataforma (alguns podem estar duplicados)

-- Verificando as origem que possuímos
select distinct origem 
from clientes;

-- Alguns clientes estão com indicacao e outros com Indicação
select count(*)
from clientes 
where origem = 'Indicação';

-- Padronizando para Indicação
update clientes
set origem = 'Indicação'
where origem = 'indicacao';

-- Padronizando nomes de origem das plataformas;
select initcap(origem) from clientes;
update clientes
set origem = initcap(origem)


-- Os emails estao seguindo um padrao diferente tambem, misturando letras maiusculas e minúsculas. irei corrigir
update clientes
set email = lower(email);

-- Aqui eu percebi que existem clientes duplicados
select * from clientes
where email = 'joao.mercon1992@gmail.com'

-- 41 clientes duplicados.
select email, count(*) as quantidade
from clientes
where email is not null
group by email
having count(*) > 1
order by quantidade desc;

-- Aqui vou precisar rodar um comando no qual eu vou remover os emails duplicados seguindo uma regra, porém nenhum dado será apagado, irei gravar em uma outra tabela.
-- Padronizando o campo act_marketing.
SELECT act_marketing, count(*)
FROM clientes
GROUP BY 1
ORDER BY 2 DESC;

BEGIN;
UPDATE clientes
SET act_marketing = CASE
    WHEN upper(trim(act_marketing)) IN ('SIM','S') THEN 'Sim'
    WHEN upper(trim(act_marketing)) IN ('NÃO','NAO','N') THEN 'Não'
    ELSE NULL
END;
SELECT act_marketing, count(*) FROM clientes GROUP BY 1; 


-- Criando a tabela de backup
CREATE TABLE clientes_duplicados (
  LIKE clientes,                 
  codigo_principal integer   NOT NULL,
  data_remocao     timestamp NOT NULL DEFAULT now(),
  motivo           text      NOT NULL
);

-- Iniciando o comando
BEGIN;

CREATE TEMP TABLE map_dup ON COMMIT DROP AS
SELECT codigo, codigo_principal
FROM (
  SELECT codigo,
         ROW_NUMBER()  OVER (PARTITION BY lower(trim(email)) ORDER BY data_cadastro, codigo) AS rn,
         FIRST_VALUE(codigo) OVER (PARTITION BY lower(trim(email)) ORDER BY data_cadastro, codigo) AS codigo_principal
  FROM clientes
) x
WHERE rn > 1;

SELECT count(*) FROM map_dup;   -- esperado: 41

INSERT INTO clientes_duplicados
SELECT c.*, m.codigo_principal, now(), 'e-mail duplicado'
FROM clientes c
JOIN map_dup m ON m.codigo = c.codigo;

UPDATE clientes p
SET act_marketing = 'Não'
WHERE p.codigo IN (
  SELECT m.codigo_principal
  FROM map_dup m
  JOIN clientes d ON d.codigo = m.codigo
  WHERE d.act_marketing = 'Não'
);

DELETE FROM clientes c
USING map_dup m
WHERE c.codigo = m.codigo;

-- conferência
SELECT (SELECT count(*) FROM clientes)            AS base,        -- esperado: 2100
       (SELECT count(*) FROM clientes_duplicados) AS duplicados;  -- esperado: 41

SELECT lower(trim(email)), count(*)
FROM clientes
GROUP BY 1
HAVING count(*) > 1;                                              -- esperado: nenhuma linha

COMMIT; 


