from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__)

# 📌 Registrar usuário
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email já registrado"}), 400

    user = User(
        name=data.get("name", "Usuário"),
        email=data["email"]
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Usuário registrado com sucesso!"}), 201


# 📌 Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if user and user.check_password(data.get("password", "")):
        token = create_access_token(identity=user.id)
        return jsonify({"access_token": token}), 200
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401


# 📌 Pegar dados do usuário logado
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    })
