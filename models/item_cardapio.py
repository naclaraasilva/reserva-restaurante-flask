from database import execute_sql


class ItemCardapioModel:

    @staticmethod
    def get_all():
        return execute_sql(
            "SELECT * FROM itens_cardapio ORDER BY nome",
            fetchall=True
        )

    @staticmethod
    def get_by_id(id_: int):
        return execute_sql(
            "SELECT * FROM itens_cardapio WHERE id = %s",
            (id_,), fetchone=True
        )

    @staticmethod
    def get_disponiveis():
        return execute_sql(
            "SELECT * FROM itens_cardapio WHERE disponivel = 1 ORDER BY nome",
            fetchall=True
        )

    @staticmethod
    def create(nome: str, descricao: str, preco: float):
        return execute_sql(
            "INSERT INTO itens_cardapio (nome, descricao, preco) VALUES (%s, %s, %s)",
            (nome, descricao, preco), commit=True
        )

    @staticmethod
    def update(id_: int, nome: str, descricao: str, preco: float, disponivel: int):
        return execute_sql(
            "UPDATE itens_cardapio SET nome=%s, descricao=%s, preco=%s, disponivel=%s WHERE id=%s",
            (nome, descricao, preco, disponivel, id_), commit=True
        )

    @staticmethod
    def delete(id_: int):
        return execute_sql(
            "DELETE FROM itens_cardapio WHERE id=%s",
            (id_,), commit=True
        )
