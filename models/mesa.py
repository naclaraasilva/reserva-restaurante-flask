from database import execute_sql


class MesaModel:

    @staticmethod
    def get_all():
        return execute_sql(
            """
            SELECT m.*, r.nome AS restaurante_nome
            FROM mesas m
            JOIN restaurantes r ON r.id = m.restaurante_id
            ORDER BY r.nome, m.numero
            """,
            fetchall=True
        )

    @staticmethod
    def get_by_id(id_: int):
        return execute_sql(
            """
            SELECT m.*, r.nome AS restaurante_nome
            FROM mesas m
            JOIN restaurantes r ON r.id = m.restaurante_id
            WHERE m.id = %s
            """,
            (id_,), fetchone=True
        )

    @staticmethod
    def get_disponiveis(restaurante_id: int = None):
        sql = """
            SELECT m.*, r.nome AS restaurante_nome
            FROM mesas m
            JOIN restaurantes r ON r.id = m.restaurante_id
            WHERE m.disponivel = 1
        """
        params = []
        if restaurante_id:
            sql += " AND m.restaurante_id = %s"
            params.append(restaurante_id)
        sql += " ORDER BY r.nome, m.numero"
        return execute_sql(sql, tuple(params), fetchall=True)

    @staticmethod
    def create(numero: int, capacidade: int, restaurante_id: int):
        return execute_sql(
            "INSERT INTO mesas (numero, capacidade, restaurante_id) VALUES (%s, %s, %s)",
            (numero, capacidade, restaurante_id), commit=True
        )

    @staticmethod
    def update(id_: int, numero: int, capacidade: int, disponivel: int, restaurante_id: int):
        return execute_sql(
            "UPDATE mesas SET numero=%s, capacidade=%s, disponivel=%s, restaurante_id=%s WHERE id=%s",
            (numero, capacidade, disponivel, restaurante_id, id_), commit=True
        )

    @staticmethod
    def set_disponivel(id_: int, disponivel: int):
        return execute_sql(
            "UPDATE mesas SET disponivel=%s WHERE id=%s",
            (disponivel, id_), commit=True
        )

    @staticmethod
    def delete(id_: int):
        return execute_sql(
            "DELETE FROM mesas WHERE id=%s",
            (id_,), commit=True
        )
