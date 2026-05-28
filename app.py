from flask import Flask, jsonify, render_template
from config import Config
from routes.cliente_routes      import cliente_bp
from routes.restaurante_routes  import restaurante_bp
from routes.mesa_routes         import mesa_bp
from routes.reserva_routes      import reserva_bp
from routes.item_cardapio_routes import item_cardapio_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Registra Blueprints
    app.register_blueprint(cliente_bp)
    app.register_blueprint(restaurante_bp)
    app.register_blueprint(mesa_bp)
    app.register_blueprint(reserva_bp)
    app.register_blueprint(item_cardapio_bp)

    # ── Handlers globais de erro ──────────────────────────────────────────────

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"erro": "Requisição inválida"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Rota não encontrada"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"erro": "Método não permitido"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"erro": "Erro interno do servidor", "detalhe": str(e)}), 500

    # ── Health-check ──────────────────────────────────────────────────────────

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    # ── Página inicial ────────────────────────────────────────────────────────

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
