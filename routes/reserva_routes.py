from flask import Blueprint, request, jsonify, render_template
from models.reserva import ReservaModel
from models.mesa import MesaModel
from models.cliente import ClienteModel
from models.item_cardapio import ItemCardapioModel
from models.restaurante import RestauranteModel
from utils.validators import validate_required_fields, parse_date, parse_time

reserva_bp = Blueprint("reserva", __name__, url_prefix="/api/reservas")


def _not_found():
    return jsonify({"erro": "Reserva não encontrada"}), 404


# verificações -> data, hora, mesa, cliente existente ou nao
def _validar_e_parsear(data: dict, exclude_id: int = None):

    required = ["cliente_id", "mesa_id", "data", "hora", "pessoas"]
    faltando = validate_required_fields(data, required)
    if faltando:
        return None, ({"erros": [f"'{f}' é obrigatório" for f in faltando]}, 422)

    try:
        data_parsed = parse_date(data["data"])
        hora_parsed = parse_time(data["hora"])
    except ValueError as exc:
        return None, ({"erro": str(exc)}, 422)

    pessoas = data["pessoas"]
    if not isinstance(pessoas, int) or pessoas < 1:
        return None, ({"erro": "'pessoas' deve ser um inteiro >= 1"}, 422)

    cliente_id = data["cliente_id"]
    mesa_id    = data["mesa_id"]

    if not ClienteModel.get_by_id(cliente_id):
        return None, ({"erro": "Cliente não encontrado"}, 404)

    mesa = MesaModel.get_by_id(mesa_id)
    if not mesa:
        return None, ({"erro": "Mesa não encontrada"}, 404)

    if pessoas > mesa["capacidade"]:
        return None, ({
            "erro": f"Número de pessoas ({pessoas}) excede a capacidade da mesa ({mesa['capacidade']})"
        }, 422)

    if ReservaModel.check_conflito(mesa_id, str(data_parsed), hora_parsed, exclude_id):
        return None, ({
            "erro": "Conflito de horário: já existe uma reserva ativa para esta mesa nesta data e hora."
        }, 409)

    return {
        "cliente_id": cliente_id,
        "mesa_id":    mesa_id,
        "data":       str(data_parsed),
        "hora":       hora_parsed,
        "pessoas":    pessoas,
    }, None


# ─── api json ────────────────────────────────────────────────────────────────

@reserva_bp.route("", methods=["GET"])
def listar():
    cliente_id = request.args.get("cliente_id", type=int)
    mesa_id    = request.args.get("mesa_id", type=int)
    data       = request.args.get("data")
    reservas   = ReservaModel.get_all(cliente_id, mesa_id, data)
    return jsonify(reservas), 200


@reserva_bp.route("/<int:id_>", methods=["GET"])
def buscar(id_):
    reserva = ReservaModel.get_by_id(id_)
    if not reserva:
        return _not_found()
    itens = ReservaModel.get_itens(id_)
    reserva["itens"] = itens
    return jsonify(reserva), 200


@reserva_bp.route("", methods=["POST"])
def criar():
    data = request.get_json(silent=True) or {}
    payload, erro = _validar_e_parsear(data)
    if erro:
        return jsonify(erro[0]), erro[1]

    new_id = ReservaModel.create(**payload)
    return jsonify({"mensagem": "Reserva criada com sucesso", "id": new_id}), 201


@reserva_bp.route("/<int:id_>", methods=["PUT"])
def atualizar(id_):
    reserva = ReservaModel.get_by_id(id_)
    if not reserva:
        return _not_found()

    if reserva["status"] == "cancelada":
        return jsonify({"erro": "Não é possível editar uma reserva cancelada"}), 422

    data = request.get_json(silent=True) or {}

    data.setdefault("cliente_id", reserva["cliente_id"])
    data.setdefault("mesa_id",    reserva["mesa_id"])
    data.setdefault("data",       str(reserva["data"]))
    data.setdefault("hora",       str(reserva["hora"]))
    data.setdefault("pessoas",    reserva["pessoas"])

    payload, erro = _validar_e_parsear(data, exclude_id=id_)
    if erro:
        return jsonify(erro[0]), erro[1]

    ReservaModel.update(id_, **payload)
    return jsonify({"mensagem": "Reserva atualizada com sucesso"}), 200


@reserva_bp.route("/<int:id_>/cancelar", methods=["PATCH"])
def cancelar(id_):
    reserva = ReservaModel.get_by_id(id_)
    if not reserva:
        return _not_found()
    if reserva["status"] == "cancelada":
        return jsonify({"erro": "Reserva já está cancelada"}), 422
    ReservaModel.cancelar(id_)
    return jsonify({"mensagem": "Reserva cancelada com sucesso"}), 200


@reserva_bp.route("/<int:id_>/concluir", methods=["PATCH"])
def concluir(id_):
    reserva = ReservaModel.get_by_id(id_)
    if not reserva:
        return _not_found()
    if reserva["status"] != "ativa":
        return jsonify({"erro": "Apenas reservas ativas podem ser concluídas"}), 422
    ReservaModel.concluir(id_)
    return jsonify({"mensagem": "Reserva concluída com sucesso"}), 200


@reserva_bp.route("/<int:id_>", methods=["DELETE"])
def deletar(id_):
    reserva = ReservaModel.get_by_id(id_)
    if not reserva:
        return _not_found()
    ReservaModel.delete(id_)
    return jsonify({"mensagem": "Reserva removida com sucesso"}), 200


# ─── N:N itens do cardápio ────────────────────────────────────────────────────

@reserva_bp.route("/<int:id_>/itens", methods=["GET"])
def listar_itens(id_):
    reserva = ReservaModel.get_by_id(id_)
    if not reserva:
        return _not_found()
    itens = ReservaModel.get_itens(id_)
    return jsonify(itens), 200


@reserva_bp.route("/<int:id_>/itens/<int:item_id>", methods=["POST"])
def adicionar_item(id_, item_id):
    reserva = ReservaModel.get_by_id(id_)
    if not reserva:
        return _not_found()

    if reserva["status"] != "ativa":
        return jsonify({"erro": "Só é possível adicionar itens a reservas ativas"}), 422

    item = ItemCardapioModel.get_by_id(item_id)
    if not item:
        return jsonify({"erro": "Item do cardápio não encontrado"}), 404

    # Valida se o item pertence ao cardápio do restaurante desta reserva
    restaurante_id = reserva["restaurante_id"]
    if not RestauranteModel.item_no_cardapio(restaurante_id, item_id):
        return jsonify({
            "erro": "Este item não pertence ao cardápio do restaurante desta reserva"
        }), 422

    data       = request.get_json(silent=True) or {}
    quantidade = data.get("quantidade", 1)
    if not isinstance(quantidade, int) or quantidade < 1:
        return jsonify({"erro": "'quantidade' deve ser um inteiro >= 1"}), 422

    ReservaModel.adicionar_item(id_, item_id, quantidade)
    return jsonify({"mensagem": "Item adicionado à reserva com sucesso"}), 200


@reserva_bp.route("/<int:id_>/itens/<int:item_id>", methods=["DELETE"])
def remover_item(id_, item_id):
    reserva = ReservaModel.get_by_id(id_)
    if not reserva:
        return _not_found()

    if not ReservaModel.item_na_reserva(id_, item_id):
        return jsonify({"erro": "Item não vinculado a esta reserva"}), 404

    ReservaModel.remover_item(id_, item_id)
    return jsonify({"mensagem": "Item removido da reserva com sucesso"}), 200


# ─── páginas HTML ─────────────────────────────────────────────────────────────

@reserva_bp.route("/pagina", methods=["GET"])
def pagina_listar():
    reservas = ReservaModel.get_all()
    clientes = ClienteModel.get_all()
    mesas    = MesaModel.get_all()
    return render_template("reservas/listar.html", reservas=reservas, clientes=clientes, mesas=mesas)


@reserva_bp.route("/pagina/<int:id_>", methods=["GET"])
def pagina_detalhe(id_):
    reserva = ReservaModel.get_by_id(id_)
    if not reserva:
        return render_template("erro.html", mensagem="Reserva não encontrada"), 404
    itens          = ReservaModel.get_itens(id_)
    # Carrega apenas os itens do cardápio do restaurante desta reserva
    itens_cardapio = RestauranteModel.get_cardapio(reserva["restaurante_id"])
    return render_template(
        "reservas/detalhe.html",
        reserva=reserva,
        itens=itens,
        itens_cardapio=itens_cardapio
    )
