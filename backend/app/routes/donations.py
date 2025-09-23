from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal
from ..extensions import db
from ..models import Donation, Campaign

donations_bp = Blueprint("donations", __name__)

# 📌 Registrar doação
@donations_bp.route("/", methods=["POST"])
@jwt_required()
def donate():
    data = request.get_json()
    user_id = get_jwt_identity()

    campaign = Campaign.query.get_or_404(data.get("campaign_id"))
    amount = Decimal(str(data.get("amount", 0)))  # 🔹 Corrigido: converter para Decimal

    if amount <= 0:
        return jsonify({"error": "Valor inválido"}), 400

    try:
        # Transação: registrar doação e atualizar campanha
        donation = Donation(user_id=user_id, campaign_id=campaign.id, amount=amount)
        campaign.collected_amount += amount  # ✅ Soma Decimal + Decimal

        db.session.add(donation)
        db.session.commit()
        return jsonify({"msg": "Doação registrada com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# 📌 Listar doações de uma campanha
@donations_bp.route("/campaign/<int:campaign_id>", methods=["GET"])
def list_donations(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    donations = [
        {
            "id": d.id,
            "amount": d.amount,
            "user": d.user.name,
            "created_at": d.created_at.isoformat()
        }
        for d in campaign.donations
    ]
    return jsonify(donations)
