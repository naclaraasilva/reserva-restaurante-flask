from flask import Blueprint, request, jsonify, render_template
from models.cliente import ClienteModel
from utils.validators import validate_email

cliente_bp = Blueprint("cliente", __name__, url_prefix="/api/clientes")


def _not_found():
    return jsonify({"erro": "Cliente não encontrado"}), 404


#api json
@cliente_bp.route("", methods=["GET"])
def listar():
    clientes = ClienteModel.get_all()
    return jsonify(clientes), 200


@cliente_bp.route("/<int:id_>", methods=["GET"])
def buscar(id_):
    cliente = ClienteModel.get_by_id(id_)
    if not cliente:
        return _not_found()
    return jsonify(cliente), 200


@cliente_bp.route("", methods=["POST"])
def criar():
    data = request.get_json(silent=True) or {}

    erros = []
    if not data.get("nome"):
        erros.append("'nome' é obrigatório")
    if not data.get("email"):
        erros.append("'email' é obrigatório")
    elif not validate_email(data["email"]):
        erros.append("'email' inválido")

    if erros:
        return jsonify({"erros": erros}), 422

    if ClienteModel.get_by_email(data["email"]):
        return jsonify({"erro": "E-mail já cadastrado"}), 409

    new_id = ClienteModel.create(
        nome=data["nome"],
        email=data["email"],
        telefone=data.get("telefone", ""),
    )
    return jsonify({"mensagem": "Cliente criado com sucesso", "id": new_id}), 201


@cliente_bp.route("/<int:id_>", methods=["PUT"])
def atualizar(id_):
    cliente = ClienteModel.get_by_id(id_)
    if not cliente:
        return _not_found()

    data = request.get_json(silent=True) or {}

    nome     = data.get("nome", cliente["nome"])
    email    = data.get("email", cliente["email"])
    telefone = data.get("telefone", cliente["telefone"])
    ativo    = data.get("ativo", cliente["ativo"])

    if not nome:
        return jsonify({"erro": "'nome' não pode ser vazio"}), 422
    if not validate_email(email):
        return jsonify({"erro": "'email' inválido"}), 422

    existente = ClienteModel.get_by_email(email)
    if existente and existente["id"] != id_:
        return jsonify({"erro": "E-mail já utilizado por outro cliente"}), 409

    ClienteModel.update(id_, nome, email, telefone, ativo)
    return jsonify({"mensagem": "Cliente atualizado com sucesso"}), 200


@cliente_bp.route("/<int:id_>", methods=["DELETE"])
def deletar(id_):
    cliente = ClienteModel.get_by_id(id_)
    if not cliente:
        return _not_found()
    try:
        ClienteModel.delete(id_)
        return jsonify({"mensagem": "Cliente removido com sucesso"}), 200
    except Exception:
        return jsonify({"erro": "Não é possível excluir: cliente possui reservas vinculadas"}), 409


@cliente_bp.route("/<int:id_>/reservas", methods=["GET"])
def reservas_do_cliente(id_):
    cliente = ClienteModel.get_by_id(id_)
    if not cliente:
        return _not_found()
    reservas = ClienteModel.get_reservas(id_)
    return jsonify({"cliente": cliente["nome"], "reservas": reservas}), 200


#pginas HTML
@cliente_bp.route("/pagina", methods=["GET"])
def pagina_listar():
    clientes = ClienteModel.get_all()
    return render_template("clientes/listar.html", clientes=clientes)


@cliente_bp.route("/pagina/<int:id_>", methods=["GET"])
def pagina_detalhe(id_):
    cliente = ClienteModel.get_by_id(id_)
    if not cliente:
        return render_template("erro.html", mensagem="Cliente não encontrado"), 404
    reservas = ClienteModel.get_reservas(id_)
    return render_template("clientes/detalhe.html", cliente=cliente, reservas=reservas)
