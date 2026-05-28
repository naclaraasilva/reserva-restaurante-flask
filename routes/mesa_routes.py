from flask import Blueprint, request, jsonify, render_template
from models.mesa import MesaModel
from models.restaurante import RestauranteModel

mesa_bp = Blueprint("mesa", __name__, url_prefix="/api/mesas")


def _not_found():
    return jsonify({"erro": "Mesa não encontrada"}), 404


#api json
@mesa_bp.route("", methods=["GET"])
def listar():
    restaurante_id = request.args.get("restaurante_id", type=int)
    apenas_disponiveis = request.args.get("disponiveis", type=str)

    if apenas_disponiveis and apenas_disponiveis.lower() == "true":
        mesas = MesaModel.get_disponiveis(restaurante_id)
    else:
        mesas = MesaModel.get_all()
        if restaurante_id:
            mesas = [m for m in mesas if m["restaurante_id"] == restaurante_id]

    return jsonify(mesas), 200


@mesa_bp.route("/<int:id_>", methods=["GET"])
def buscar(id_):
    mesa = MesaModel.get_by_id(id_)
    if not mesa:
        return _not_found()
    return jsonify(mesa), 200


@mesa_bp.route("", methods=["POST"])
def criar():
    data = request.get_json(silent=True) or {}

    erros = []
    if data.get("numero") is None:
        erros.append("'numero' é obrigatório")
    if data.get("capacidade") is None:
        erros.append("'capacidade' é obrigatório")
    elif not isinstance(data["capacidade"], int) or data["capacidade"] < 1:
        erros.append("'capacidade' deve ser um inteiro >= 1")
    if not data.get("restaurante_id"):
        erros.append("'restaurante_id' é obrigatório")

    if erros:
        return jsonify({"erros": erros}), 422

    if not RestauranteModel.get_by_id(data["restaurante_id"]):
        return jsonify({"erro": "Restaurante não encontrado"}), 404

    new_id = MesaModel.create(
        numero=data["numero"],
        capacidade=data["capacidade"],
        restaurante_id=data["restaurante_id"],
    )
    return jsonify({"mensagem": "Mesa criada com sucesso", "id": new_id}), 201


@mesa_bp.route("/<int:id_>", methods=["PUT"])
def atualizar(id_):
    mesa = MesaModel.get_by_id(id_)
    if not mesa:
        return _not_found()

    data = request.get_json(silent=True) or {}

    numero         = data.get("numero", mesa["numero"])
    capacidade     = data.get("capacidade", mesa["capacidade"])
    disponivel     = data.get("disponivel", mesa["disponivel"])
    restaurante_id = data.get("restaurante_id", mesa["restaurante_id"])

    if not isinstance(capacidade, int) or capacidade < 1:
        return jsonify({"erro": "'capacidade' deve ser um inteiro >= 1"}), 422

    if not RestauranteModel.get_by_id(restaurante_id):
        return jsonify({"erro": "Restaurante não encontrado"}), 404

    MesaModel.update(id_, numero, capacidade, disponivel, restaurante_id)
    return jsonify({"mensagem": "Mesa atualizada com sucesso"}), 200


@mesa_bp.route("/<int:id_>", methods=["DELETE"])
def deletar(id_):
    mesa = MesaModel.get_by_id(id_)
    if not mesa:
        return _not_found()
    try:
        MesaModel.delete(id_)
        return jsonify({"mensagem": "Mesa removida com sucesso"}), 200
    except Exception:
        return jsonify({"erro": "Não é possível excluir: mesa possui reservas vinculadas"}), 409


@mesa_bp.route("/<int:id_>/disponibilidade", methods=["PATCH"])
def alterar_disponibilidade(id_):
    mesa = MesaModel.get_by_id(id_)
    if not mesa:
        return _not_found()
    data = request.get_json(silent=True) or {}
    disponivel = data.get("disponivel")
    if disponivel is None:
        return jsonify({"erro": "Campo 'disponivel' é obrigatório"}), 422
    MesaModel.set_disponivel(id_, 1 if disponivel else 0)
    status = "disponível" if disponivel else "indisponível"
    return jsonify({"mensagem": f"Mesa marcada como {status}"}), 200


#paginas HTML
@mesa_bp.route("/pagina", methods=["GET"])
def pagina_listar():
    mesas = MesaModel.get_all()
    restaurantes = RestauranteModel.get_all()
    return render_template("mesas/listar.html", mesas=mesas, restaurantes=restaurantes)


@mesa_bp.route("/pagina/<int:id_>", methods=["GET"])
def pagina_detalhe(id_):
    mesa = MesaModel.get_by_id(id_)
    if not mesa:
        return render_template("erro.html", mensagem="Mesa não encontrada"), 404
    return render_template("mesas/detalhe.html", mesa=mesa)
