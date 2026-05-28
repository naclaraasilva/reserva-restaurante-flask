from flask import Blueprint, request, jsonify, render_template
from models.restaurante import RestauranteModel
from models.item_cardapio import ItemCardapioModel

restaurante_bp = Blueprint("restaurante", __name__, url_prefix="/api/restaurantes")


def _not_found():
    return jsonify({"erro": "Restaurante não encontrado"}), 404


# ─── api json ────────────────────────────────────────────────────────────────

@restaurante_bp.route("", methods=["GET"])
def listar():
    restaurantes = RestauranteModel.get_all()
    return jsonify(restaurantes), 200


@restaurante_bp.route("/<int:id_>", methods=["GET"])
def buscar(id_):
    restaurante = RestauranteModel.get_by_id(id_)
    if not restaurante:
        return _not_found()
    return jsonify(restaurante), 200


@restaurante_bp.route("", methods=["POST"])
def criar():
    data = request.get_json(silent=True) or {}

    if not data.get("nome"):
        return jsonify({"erro": "O campo 'nome' é obrigatório"}), 422

    new_id = RestauranteModel.create(
        nome=data["nome"],
        endereco=data.get("endereco", ""),
        telefone=data.get("telefone", ""),
    )
    return jsonify({"mensagem": "Restaurante criado com sucesso", "id": new_id}), 201


@restaurante_bp.route("/<int:id_>", methods=["PUT"])
def atualizar(id_):
    restaurante = RestauranteModel.get_by_id(id_)
    if not restaurante:
        return _not_found()

    data = request.get_json(silent=True) or {}

    nome     = data.get("nome", restaurante["nome"])
    endereco = data.get("endereco", restaurante["endereco"])
    telefone = data.get("telefone", restaurante["telefone"])
    ativo    = data.get("ativo", restaurante["ativo"])

    if not nome:
        return jsonify({"erro": "O campo 'nome' não pode ser vazio"}), 422

    RestauranteModel.update(id_, nome, endereco, telefone, ativo)
    return jsonify({"mensagem": "Restaurante atualizado com sucesso"}), 200


@restaurante_bp.route("/<int:id_>", methods=["DELETE"])
def deletar(id_):
    restaurante = RestauranteModel.get_by_id(id_)
    if not restaurante:
        return _not_found()
    try:
        RestauranteModel.delete(id_)
        return jsonify({"mensagem": "Restaurante removido com sucesso"}), 200
    except Exception:
        return jsonify({"erro": "Não é possível excluir: restaurante possui mesas vinculadas"}), 409


@restaurante_bp.route("/<int:id_>/mesas", methods=["GET"])
def mesas_do_restaurante(id_):
    restaurante = RestauranteModel.get_by_id(id_)
    if not restaurante:
        return _not_found()
    mesas = RestauranteModel.get_mesas(id_)
    return jsonify({"restaurante": restaurante["nome"], "mesas": mesas}), 200


# ─── N:N cardápio do restaurante ─────────────────────────────────────────────

@restaurante_bp.route("/<int:id_>/cardapio", methods=["GET"])
def listar_cardapio(id_):
    """Lista todos os itens do cardápio vinculados ao restaurante."""
    restaurante = RestauranteModel.get_by_id(id_)
    if not restaurante:
        return _not_found()
    itens = RestauranteModel.get_cardapio(id_)
    return jsonify({"restaurante": restaurante["nome"], "cardapio": itens}), 200


@restaurante_bp.route("/<int:id_>/cardapio/<int:item_id>", methods=["POST"])
def adicionar_item_cardapio(id_, item_id):
    """Vincula um item do cardápio ao restaurante."""
    restaurante = RestauranteModel.get_by_id(id_)
    if not restaurante:
        return _not_found()

    item = ItemCardapioModel.get_by_id(item_id)
    if not item:
        return jsonify({"erro": "Item do cardápio não encontrado"}), 404

    data       = request.get_json(silent=True) or {}
    disponivel = data.get("disponivel", 1)
    if disponivel not in (0, 1):
        return jsonify({"erro": "'disponivel' deve ser 0 ou 1"}), 422

    RestauranteModel.adicionar_item_cardapio(id_, item_id, disponivel)
    return jsonify({"mensagem": "Item adicionado ao cardápio do restaurante com sucesso"}), 200


@restaurante_bp.route("/<int:id_>/cardapio/<int:item_id>", methods=["DELETE"])
def remover_item_cardapio(id_, item_id):
    """Remove o vínculo de um item do cardápio com o restaurante."""
    restaurante = RestauranteModel.get_by_id(id_)
    if not restaurante:
        return _not_found()

    if not RestauranteModel.item_no_cardapio(id_, item_id):
        return jsonify({"erro": "Item não vinculado ao cardápio deste restaurante"}), 404

    RestauranteModel.remover_item_cardapio(id_, item_id)
    return jsonify({"mensagem": "Item removido do cardápio do restaurante com sucesso"}), 200


# ─── páginas HTML ─────────────────────────────────────────────────────────────

@restaurante_bp.route("/pagina", methods=["GET"])
def pagina_listar():
    restaurantes = RestauranteModel.get_all()
    return render_template("restaurantes/listar.html", restaurantes=restaurantes)


@restaurante_bp.route("/pagina/<int:id_>", methods=["GET"])
def pagina_detalhe(id_):
    restaurante = RestauranteModel.get_by_id(id_)
    if not restaurante:
        return render_template("erro.html", mensagem="Restaurante não encontrado"), 404
    mesas    = RestauranteModel.get_mesas(id_)
    cardapio = RestauranteModel.get_cardapio(id_)
    # IDs dos itens já vinculados para filtrar o dropdown de adição
    ids_vinculados = {i["id"] for i in cardapio}
    todos_itens    = [i for i in ItemCardapioModel.get_all() if i["id"] not in ids_vinculados]
    return render_template(
        "restaurantes/detalhe.html",
        restaurante=restaurante,
        mesas=mesas,
        cardapio=cardapio,
        todos_itens=todos_itens
    )
