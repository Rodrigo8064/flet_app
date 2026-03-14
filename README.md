# 💰 Finanças Pessoais — App Mobile com Flet

## Instalação

```bash
pip install flet flet_chart
```

## Como rodar

```bash
flet run
```

Para rodar no navegador (modo web acessível na rede local):
```bash
flet run --web --port 8080 main.py
```
Depois acesse `http://SEU_IP:8080`.

---

## Funcionalidades

### 📊 Dashboard
- **Saldo atual** com total de receitas e despesas
- **Gráfico de linha** mostrando historico do pratrimônio
- **Top 5 categorias** de despesas com barra de progresso
- **Últimas 5 movimentações**

### 📋 Histórico
- Lista completa de todas as movimentações
- Filtro por tipo: Todos / Receita / Despesa
- Botão para excluir movimentação

### ➕ Nova Movimentação
Campos:
- **Data** (padrão: hoje)
- **Modo de pagamento** Cartão / Pix
- **Tipo**: Despesa / Receita
- **Valor**
- **Cartão**: Nubank, Inter, Bradesco, Itaú, C6 Bank, Outro
- **Categoria**: Alimentação, Viagem, Outros....
- **Observação** (opcional)

### 💳 Contas
- Card visual com gradiente para cada Conta com movimentações
- Mostra: saldo, entradas, saídas e quantidade de movimentações

---

## Dados
Os dados são salvos automaticamente no arquivo `financas.db` 
na mesma pasta do `main.py`.

---