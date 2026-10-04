create table clientes(
codigo integer primary key,
nome varchar(30), 
email varchar(60),
telefone varchar(16),
cidade varchar(30),
uf char(2),
data_cadastro date,
origem varchar,
act_marketing char(3)
)

ALTER TABLE clientes
ADD CONSTRAINT uq_clientes_email UNIQUE (email);


create table pedidos_ecommerce(
    id_pedido integer primary key,
    data_pedido date,
    email varchar(60) not null,
    canal_venda varchar(20),
    utm_source varchar(20),
    utm_medium varchar(20),
    utm_campaign varchar(40),
    cupom varchar (20), 
    valor_produtos decimal(10,2),
    desconto decimal(10,2),
    frete decimal(10,2),
    valor_total decimal(10,2),
    status varchar(20)

)

ALTER TABLE pedidos_ecommerce
ADD CONSTRAINT fk_pedidos_cliente
FOREIGN KEY (email)
REFERENCES clientes(email);