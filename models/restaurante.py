from database import execute_sql


class RestauranteModel:

    @staticmethod
    def get_all():
        return execute_sql(
            "SELECT * FROM restaurantes ORDER BY nome",
            fetchall=True
        )

    @staticmethod
    def get_by_id(id_: int):
        return execute_sql(
            "SELECT * FROM restaurantes WHERE id = %s",
            (id_,), fetchone=True
        )

    @staticmethod
    def create(nome: str, endereco: str, telefone: str):
        return execute_sql(
            "INSERT INTO restaurantes (nome, endereco, telefone) VALUES (%s, %s, %s)",
            (nome, endereco, telefone), commit=True
        )

    @staticmethod
    def update(id_: int, nome: str, endereco: str, telefone: str, ativo: int):
        return execute_sql(
            "UPDATE restaurantes SET nome=%s, endereco=%s, telefone=%s, ativo=%s WHERE id=%s",
            (nome, endereco, telefone, ativo, id_), commit=True
        )

    @staticmethod
    def delete(id_: int):
        return execute_sql(
            "DELETE FROM restaurantes WHERE id=%s",
            (id_,), commit=True
        )

    @staticmethod
    def get_mesas(restaurante_id: int):
        return execute_sql(
            """
            SELECT * FROM mesas
            WHERE restaurante_id = %s
            ORDER BY numero
            """,
            (restaurante_id,), fetchall=True
        )

    # ─── N:N com itens_cardapio ───────────────────────────────────────────────

    @staticmethod
    def get_cardapio(restaurante_id: int):
        """Retorna todos os itens do cardápio vinculados ao restaurante."""
        return execute_sql(
            """
            SELECT ic.id, ic.nome, ic.descricao, ic.preco, ic.disponivel,
                   ri.disponivel AS disponivel_no_restaurante
            FROM restaurante_item ri
            JOIN itens_cardapio ic ON ic.id = ri.item_cardapio_id
            WHERE ri.restaurante_id = %s
            ORDER BY ic.nome
            """,
            (restaurante_id,), fetchall=True
        )

    @staticmethod
    def adicionar_item_cardapio(restaurante_id: int, item_id: int, disponivel: int = 1):
        """Vincula um item do cardápio ao restaurante."""
        return execute_sql(
            """
            INSERT INTO restaurante_item (restaurante_id, item_cardapio_id, disponivel)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE disponivel = %s
            """,
            (restaurante_id, item_id, disponivel, disponivel), commit=True
        )

    @staticmethod
    def remover_item_cardapio(restaurante_id: int, item_id: int):
        """Desvincula um item do cardápio do restaurante."""
        return execute_sql(
            "DELETE FROM restaurante_item WHERE restaurante_id=%s AND item_cardapio_id=%s",
            (restaurante_id, item_id), commit=True
        )

    @staticmethod
    def item_no_cardapio(restaurante_id: int, item_id: int):
        """Verifica se um item pertence ao cardápio do restaurante."""
        return execute_sql(
            """
            SELECT * FROM restaurante_item
            WHERE restaurante_id = %s AND item_cardapio_id = %s
            """,
            (restaurante_id, item_id), fetchone=True
        )
