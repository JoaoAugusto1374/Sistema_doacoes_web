from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Campaign, User, Donation
from flask_cors import cross_origin

campaigns_bp = Blueprint("campaigns", __name__)

# 📌 Listar campanhas (com paginação)
@campaigns_bp.route("/", methods=["GET"])
def list_campaigns():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    pagination = Campaign.query.paginate(page=page, per_page=per_page, error_out=False)
    campaigns = [{
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "goal_amount": str(c.goal_amount),
        "collected_amount": str(c.collected_amount),
        "is_active": c.is_active,
        "created_at": c.created_at.isoformat()
    } for c in pagination.items]

    return jsonify({
        "items": campaigns,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })

# 📌 Criar campanha
@campaigns_bp.route("/", methods=["POST"])
@jwt_required()
def create_campaign():
    data = request.get_json()
    user_id = get_jwt_identity()

    campaign = Campaign(
        owner_id=user_id,
        title=data.get("title"),
        description=data.get("description"),
        goal_amount=data.get("goal_amount", 0)
    )
    db.session.add(campaign)
    db.session.commit()

    return jsonify({"msg": "Campanha criada!", "id": campaign.id}), 201

# 📌 Detalhar campanha
@campaigns_bp.route("/<int:campaign_id>", methods=["GET"])
def get_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return jsonify({
        "id": campaign.id,
        "owner_id": campaign.owner_id,
        "title": campaign.title,
        "description": campaign.description,
        "goal_amount": str(campaign.goal_amount),
        "collected_amount": str(campaign.collected_amount),
        "is_active": campaign.is_active,
        "created_at": campaign.created_at.isoformat()
    })

# 📌 Editar campanha (apenas dono)
@campaigns_bp.route("/<int:campaign_id>", methods=["PUT"])
@jwt_required()
def update_campaign(campaign_id):
    user_id = int(get_jwt_identity())
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.owner_id != user_id:
        return jsonify({"error": "Você não tem permissão para editar esta campanha"}), 403

    data = request.get_json()
    campaign.title = data.get("title", campaign.title)
    campaign.description = data.get("description", campaign.description)
    campaign.goal_amount = data.get("goal_amount", campaign.goal_amount)

    db.session.commit()
    return jsonify({"msg": "Campanha atualizada com sucesso!"})

# 📌 Deletar campanha (apenas dono)
@campaigns_bp.route("/<int:campaign_id>", methods=["DELETE"])
@jwt_required()
@cross_origin(origins="http://127.0.0.1:8000", supports_credentials=True)
def delete_campaign(campaign_id):
    user_id = get_jwt_identity()
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.owner_id != int(user_id):
        return jsonify({"error": "Você não tem permissão para excluir esta campanha"}), 403

    Donation.query.filter_by(campaign_id=campaign.id).delete()

    db.session.delete(campaign)
    db.session.commit()
    return jsonify({"msg": "Campanha excluída com sucesso!"})
