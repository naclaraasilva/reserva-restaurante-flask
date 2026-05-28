from database import execute_sql


class ReservaModel:

    @staticmethod
    def get_all(cliente_id: int = None, mesa_id: int = None, data: str = None):
        sql = """
            SELECT
                r.id, r.data, r.hora, r.pessoas, r.status, r.criado_em,
                c.id   AS cliente_id,
                c.nome AS cliente_nome,
                c.email AS cliente_email,
                m.id   AS mesa_id,
                m.numero AS mesa_numero,
                m.capacidade AS mesa_capacidade,
                re.id   AS restaurante_id,
                re.nome AS restaurante_nome
            FROM reservas r
            JOIN clientes c ON c.id = r.cliente_id
            JOIN mesas m    ON m.id = r.mesa_id
            JOIN restaurantes re ON re.id = m.restaurante_id
            WHERE 1=1
        """
        params = []
        if cliente_id:
            sql += " AND r.cliente_id = %s"
            params.append(cliente_id)
        if mesa_id:
            sql += " AND r.mesa_id = %s"
            params.append(mesa_id)
        if data:
            sql += " AND r.data = %s"
            params.append(data)
        sql += " ORDER BY r.data DESC, r.hora DESC"
        return execute_sql(sql, tuple(params), fetchall=True)

    @staticmethod
    def get_by_id(id_: int):
        return execute_sql(
            """
            SELECT
                r.id, r.data, r.hora, r.pessoas, r.status, r.criado_em,
                c.id   AS cliente_id,
                c.nome AS cliente_nome,
                c.email AS cliente_email,
                m.id   AS mesa_id,
                m.numero AS mesa_numero,
                m.capacidade AS mesa_capacidade,
                re.id   AS restaurante_id,
                re.nome AS restaurante_nome
            FROM reservas r
            JOIN clientes c ON c.id = r.cliente_id
            JOIN mesas m    ON m.id = r.mesa_id
            JOIN restaurantes re ON re.id = m.restaurante_id
            WHERE r.id = %s
            """,
            (id_,), fetchone=True
        )

    @staticmethod
    def check_conflito(mesa_id: int, data: str, hora: str, exclude_id: int = None) -> bool:
        """Verifica se já existe reserva ativa para essa mesa na mesma data e hora."""
        sql = """
            SELECT id FROM reservas
            WHERE mesa_id = %s
              AND data = %s
              AND hora = %s
              AND status = 'ativa'
        """
        params = [mesa_id, data, hora]
        if exclude_id:
            sql += " AND id != %s"
            params.append(exclude_id)
        result = execute_sql(sql, tuple(params), fetchone=True)
        return result is not None

    @staticmethod
    def create(cliente_id: int, mesa_id: int, data: str, hora: str, pessoas: int):
        return execute_sql(
            "INSERT INTO reservas (cliente_id, mesa_id, data, hora, pessoas) VALUES (%s, %s, %s, %s, %s)",
            (cliente_id, mesa_id, data, hora, pessoas), commit=True
        )

    @staticmethod
    def update(id_: int, cliente_id: int, mesa_id: int, data: str, hora: str, pessoas: int):
        return execute_sql(
            "UPDATE reservas SET cliente_id=%s, mesa_id=%s, data=%s, hora=%s, pessoas=%s WHERE id=%s",
            (cliente_id, mesa_id, data, hora, pessoas, id_), commit=True
        )

    @staticmethod
    def cancelar(id_: int):
        return execute_sql(
            "UPDATE reservas SET status='cancelada' WHERE id=%s",
            (id_,), commit=True
        )

    @staticmethod
    def concluir(id_: int):
        return execute_sql(
            "UPDATE reservas SET status='concluida' WHERE id=%s",
            (id_,), commit=True
        )

    @staticmethod
    def delete(id_: int):
        return execute_sql(
            "DELETE FROM reservas WHERE id=%s",
            (id_,), commit=True
        )

    # ─── N:N com itens_cardapio ───────────────────────────────────────────────

    @staticmethod
    def get_itens(reserva_id: int):
        return execute_sql(
            """
            SELECT ic.id, ic.nome, ic.preco, ri.quantidade
            FROM reserva_item ri
            JOIN itens_cardapio ic ON ic.id = ri.item_cardapio_id
            WHERE ri.reserva_id = %s
            ORDER BY ic.nome
            """,
            (reserva_id,), fetchall=True
        )

    @staticmethod
    def adicionar_item(reserva_id: int, item_id: int, quantidade: int = 1):
        return execute_sql(
            """
            INSERT INTO reserva_item (reserva_id, item_cardapio_id, quantidade)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantidade = quantidade + %s
            """,
            (reserva_id, item_id, quantidade, quantidade), commit=True
        )

    @staticmethod
    def remover_item(reserva_id: int, item_id: int):
        return execute_sql(
            "DELETE FROM reserva_item WHERE reserva_id=%s AND item_cardapio_id=%s",
            (reserva_id, item_id), commit=True
        )

    @staticmethod
    def item_na_reserva(reserva_id: int, item_id: int):
        return execute_sql(
            "SELECT * FROM reserva_item WHERE reserva_id=%s AND item_cardapio_id=%s",
            (reserva_id, item_id), fetchone=True
        )
