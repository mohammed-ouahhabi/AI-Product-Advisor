from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from .extensions import db
from .models import Product, Review, User
from .services import aggregate_statistics, analyze_sentiment, build_recommendations

api = Blueprint('api', __name__, url_prefix='/api')


@api.get('/health')
def health():
    return jsonify({'status': 'ok'})


@api.post('/auth/register')
def register():
    data = request.get_json(force=True)
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()

    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'password must be at least 6 characters'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email already exists'}), 409

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()}), 201


@api.post('/auth/login')
def login():
    data = request.get_json(force=True)
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'invalid credentials'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()})


@api.get('/auth/me')
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'user not found'}), 404
    return jsonify(user.to_dict())


@api.get('/products')
@jwt_required()
def list_products():
    return jsonify([p.to_dict() for p in Product.query.order_by(Product.created_at.desc()).all()])


@api.post('/products')
@jwt_required()
def create_product():
    data = request.get_json(force=True)
    name = (data.get('name') or '').strip()
    category = (data.get('category') or '').strip()
    if not name or not category:
        return jsonify({'error': 'name and category are required'}), 400

    product = Product(name=name, category=category)
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@api.delete('/products/<int:product_id>')
@jwt_required()
def delete_product(product_id: int):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'product deleted'})


@api.get('/products/<int:product_id>/reviews')
@jwt_required()
def list_reviews(product_id: int):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'product not found'}), 404
    return jsonify([r.to_dict() for r in Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()])


@api.post('/products/<int:product_id>/reviews')
@jwt_required()
def create_review(product_id: int):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'product not found'}), 404

    data = request.get_json(force=True)
    text = (data.get('text') or '').strip()
    rating = data.get('rating')
    if not text or rating is None:
        return jsonify({'error': 'text and rating are required'}), 400
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'rating must be an integer between 1 and 5'}), 400

    sentiment, score = analyze_sentiment(text)
    review = Review(
        product_id=product_id,
        text=text,
        rating=rating,
        sentiment=sentiment,
        sentiment_score=score,
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201


@api.delete('/reviews/<int:review_id>')
@jwt_required()
def delete_review(review_id: int):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'review not found'}), 404
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'review deleted'})


@api.get('/products/<int:product_id>/stats')
@jwt_required()
def product_stats(product_id: int):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'product not found'}), 404

    reviews = Review.query.filter_by(product_id=product_id).all()
    return jsonify(aggregate_statistics(reviews))


@api.get('/products/<int:product_id>/recommendations')
@jwt_required()
def product_recommendations(product_id: int):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'product not found'}), 404

    negative_reviews = Review.query.filter_by(product_id=product_id, sentiment='negative').all()
    payload = build_recommendations([r.text for r in negative_reviews])
    return jsonify(payload)
