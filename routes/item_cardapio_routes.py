from flask import Blueprint, request, jsonify, render_template
from models.item_cardapio import ItemCardapioModel

item_cardapio_bp = Blueprint("item_cardapio", __name__, url_prefix="/api/itens-cardapio")


def _not_found():
    return jsonify({"erro": "Item do cardápio não encontrado"}), 404


#api json
@item_cardapio_bp.route("", methods=["GET"])
def listar():
    apenas_disponiveis = request.args.get("disponiveis", "").lower() == "true"
    if apenas_disponiveis:
        itens = ItemCardapioModel.get_disponiveis()
    else:
        itens = ItemCardapioModel.get_all()
    return jsonify(itens), 200


@item_cardapio_bp.route("/<int:id_>", methods=["GET"])
def buscar(id_):
    item = ItemCardapioModel.get_by_id(id_)
    if not item:
        return _not_found()
    return jsonify(item), 200


@item_cardapio_bp.route("", methods=["POST"])
def criar():
    data = request.get_json(silent=True) or {}

    erros = []
    if not data.get("nome"):
        erros.append("'nome' é obrigatório")
    if data.get("preco") is None:
        erros.append("'preco' é obrigatório")
    elif not isinstance(data["preco"], (int, float)) or data["preco"] < 0:
        erros.append("'preco' deve ser um número >= 0")

    if erros:
        return jsonify({"erros": erros}), 422

    new_id = ItemCardapioModel.create(
        nome=data["nome"],
        descricao=data.get("descricao", ""),
        preco=data["preco"],
    )
    return jsonify({"mensagem": "Item criado com sucesso", "id": new_id}), 201


@item_cardapio_bp.route("/<int:id_>", methods=["PUT"])
def atualizar(id_):
    item = ItemCardapioModel.get_by_id(id_)
    if not item:
        return _not_found()

    data = request.get_json(silent=True) or {}

    nome       = data.get("nome", item["nome"])
    descricao  = data.get("descricao", item["descricao"])
    preco      = data.get("preco", item["preco"])
    disponivel = data.get("disponivel", item["disponivel"])

    if not nome:
        return jsonify({"erro": "'nome' não pode ser vazio"}), 422
    if not isinstance(preco, (int, float)) or preco < 0:
        return jsonify({"erro": "'preco' deve ser um número >= 0"}), 422

    ItemCardapioModel.update(id_, nome, descricao, preco, disponivel)
    return jsonify({"mensagem": "Item atualizado com sucesso"}), 200


@item_cardapio_bp.route("/<int:id_>", methods=["DELETE"])
def deletar(id_):
    item = ItemCardapioModel.get_by_id(id_)
    if not item:
        return _not_found()
    try:
        ItemCardapioModel.delete(id_)
        return jsonify({"mensagem": "Item removido com sucesso"}), 200
    except Exception:
        return jsonify({"erro": "Não é possível excluir: item vinculado a reservas"}), 409


#paginas HTML
@item_cardapio_bp.route("/pagina", methods=["GET"])
def pagina_listar():
    itens = ItemCardapioModel.get_all()
    return render_template("cardapio/listar.html", itens=itens)


@item_cardapio_bp.route("/pagina/<int:id_>", methods=["GET"])
def pagina_detalhe(id_):
    item = ItemCardapioModel.get_by_id(id_)
    if not item:
        return render_template("erro.html", mensagem="Item não encontrado"), 404
    return render_template("cardapio/detalhe.html", item=item)
