from database import execute_sql


class ClienteModel:

    @staticmethod
    def get_all():
        return execute_sql(
            "SELECT * FROM clientes ORDER BY nome",
            fetchall=True
        )

    @staticmethod
    def get_by_id(id_: int):
        return execute_sql(
            "SELECT * FROM clientes WHERE id = %s",
            (id_,), fetchone=True
        )

    @staticmethod
    def get_by_email(email: str):
        return execute_sql(
            "SELECT * FROM clientes WHERE email = %s",
            (email,), fetchone=True
        )

    @staticmethod
    def create(nome: str, email: str, telefone: str):
        return execute_sql(
            "INSERT INTO clientes (nome, email, telefone) VALUES (%s, %s, %s)",
            (nome, email, telefone), commit=True
        )

    @staticmethod
    def update(id_: int, nome: str, email: str, telefone: str, ativo: int):
        return execute_sql(
            "UPDATE clientes SET nome=%s, email=%s, telefone=%s, ativo=%s WHERE id=%s",
            (nome, email, telefone, ativo, id_), commit=True
        )

    @staticmethod
    def delete(id_: int):
        return execute_sql(
            "DELETE FROM clientes WHERE id=%s",
            (id_,), commit=True
        )

    @staticmethod
    def get_reservas(cliente_id: int):
        return execute_sql(
            """
            SELECT r.id, r.data, r.hora, r.pessoas, r.status,
                   m.numero AS mesa_numero, m.capacidade,
                   re.nome AS restaurante_nome
            FROM reservas r
            JOIN mesas m ON m.id = r.mesa_id
            JOIN restaurantes re ON re.id = m.restaurante_id
            WHERE r.cliente_id = %s
            ORDER BY r.data DESC, r.hora DESC
            """,
            (cliente_id,), fetchall=True
        )
