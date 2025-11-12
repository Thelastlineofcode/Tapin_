import requests
# Eventbrite Houston endpoint moved below after app initialization to ensure
# Flask `app`, `request` and `jsonify` are available when the route is defined.
from flask import Flask, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from auth import token_for
from flask_cors import CORS
from datetime import datetime
import os
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import smtplib
from email.message import EmailMessage


app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
# Load .env from repository root in development if python-dotenv is installed
try:
    from dotenv import load_dotenv

    repo_root = os.path.abspath(os.path.join(base_dir, '..'))
    load_dotenv(os.path.join(repo_root, '.env'))
except Exception:
    # python-dotenv not installed or .env missing; proceed with environment variables
    pass

# Allow overriding the database URL via environment (useful for CI or production)
default_db = 'sqlite:///' + os.path.join(base_dir, 'data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', default_db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Supabase connection pooling configuration for transaction mode (port 6543)
# Configure SQLAlchemy engine options; adapt connect_args by driver
db_url = app.config['SQLALCHEMY_DATABASE_URI']
engine_options = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 5,
    'max_overflow': 10,
}

# Use PostgreSQL-specific connect args only when using psycopg2
if isinstance(db_url, str) and db_url.lower().startswith('postgresql'):
    engine_options['connect_args'] = {
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000',
    }
elif isinstance(db_url, str) and db_url.lower().startswith('sqlite'):
    # SQLite does not accept the above options; leave empty or set sqlite-specific options
    engine_options['connect_args'] = {}

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
# Secret key used for serializer tokens and other Flask features
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', 'dev-salt')

CORS(app)

db = SQLAlchemy(app)
jwt = JWTManager(app)


def _warn_on_default_secrets():
    """Log a warning if important secret env vars are left at their dev defaults.

    This is only advisory and will not stop the app from running. It's helpful
    for local dev and in CI to call out missing secret configuration.
    """
    defaults = {
        'SECRET_KEY': 'dev-secret-key',
        'SECURITY_PASSWORD_SALT': 'dev-salt',
    }
    missing = []
    for key, default_val in defaults.items():
        val = os.environ.get(key, app.config.get(key))
        if not val or (isinstance(val, str) and val == default_val):
            missing.append(key)
    # JWT_SECRET_KEY may default to SECRET_KEY; still warn if it's the same as the dev key
    jwt_key = os.environ.get('JWT_SECRET_KEY', app.config.get('JWT_SECRET_KEY'))
    if not jwt_key or jwt_key == app.config.get('SECRET_KEY') == defaults['SECRET_KEY']:
        missing.append('JWT_SECRET_KEY')

    if missing:
        app.logger.warning(
            "Missing or default secrets detected: %s.\n"
            "For local dev copy `.env.sample` -> `.env` and set strong values."
            " See backend/CONFIG.md for details.",
            ', '.join(sorted(set(missing)))
        )


_warn_on_default_secrets()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # simple role column for basic RBAC (default: "user")
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "email": self.email}


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(100), nullable=True)  # Community, Environment, Education, Health, Animals
    image_url = db.Column(db.String(500), nullable=True)  # URL to listing image
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "category": self.category,
            "image_url": self.image_url,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Item(db.Model):
    """Simple persistent items for the MVP /api/items endpoints."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class SignUp(db.Model):
    """Track volunteer sign-ups for listings."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, declined, cancelled
    message = db.Column(db.Text)  # Optional message from volunteer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add unique constraint to prevent duplicate sign-ups
    __table_args__ = (db.UniqueConstraint('user_id', 'listing_id', name='_user_listing_uc'),)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "listing_id": self.listing_id,
            "status": self.status,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Review(db.Model):
    """User reviews for listings."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add unique constraint to prevent multiple reviews from same user
    __table_args__ = (db.UniqueConstraint('user_id', 'listing_id', name='_user_listing_review_uc'),)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "listing_id": self.listing_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def get_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])


# Ensure database tables exist when the app starts. Using app.app_context()
# is more robust than the before_first_request decorator which may not be
# available in all runtime contexts.
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return jsonify({"message": "Tapin Backend API Root"})


@app.route('/api/health', methods=['GET'])
def api_health():
    """Enhanced health check including database connectivity."""
    health_status = {"status": "ok", "components": {}}

    # Check database connection
    try:
        db.session.execute(db.text('SELECT 1'))
        health_status["components"]["database"] = {
            "status": "connected",
            "uri_prefix": app.config['SQLALCHEMY_DATABASE_URI'][:20] + "...",
            "pool_size": db.engine.pool.size() if hasattr(db.engine.pool, 'size') else 'N/A'
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        return jsonify(health_status), 503

    return jsonify(health_status), 200


@app.route('/api/items', methods=['GET'])
def api_list_items():
    # Return all items from the database
    items = Item.query.order_by(Item.id.asc()).all()
    return jsonify({"items": [i.to_dict() for i in items]}), 200


@app.route('/api/items', methods=['POST'])
@jwt_required()
def api_create_item():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({"error": "name required"}), 400
    item = Item(name=name, description=data.get('description'))
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "user already exists"}), 400
    pw_hash = generate_password_hash(password)
    user = User(email=email, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    # return both access and refresh tokens (identity stored as string)
    from auth import token_pair

    tokens = token_pair(user)
    return jsonify({"message": "user created", "user": user.to_dict(), **tokens}), 201


@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401
    # return both access and refresh tokens to the client
    from auth import token_pair

    tokens = token_pair(user)
    return jsonify({"message": "login successful", "user": user.to_dict(), **tokens})


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Exchange a valid refresh token for a new access token."""
    uid = get_jwt_identity()
    try:
        uid_int = int(uid)
    except Exception:
        uid_int = uid
    user = db.session.get(User, uid_int)
    if not user:
        return jsonify({"error": "user not found"}), 404
    access_token = token_for(uid_int)
    return jsonify({"access_token": access_token})


@app.route('/me', methods=['GET'])
@jwt_required()
def me():
    uid = get_jwt_identity()
    # convert back to int because tokens store identity as string
    try:
        uid_int = int(uid)
    except Exception:
        uid_int = uid
    # Use Session.get() which is the modern SQLAlchemy API (avoids LegacyAPIWarning)
    user = db.session.get(User, uid_int)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"user": user.to_dict()})


def send_reset_email(to_email, reset_url):
    smtp_host = os.environ.get('SMTP_HOST')
    if not smtp_host:
        return False, 'SMTP not configured'
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    use_tls = os.environ.get('SMTP_USE_TLS', 'true').lower() in ('1', 'true', 'yes')

    msg = EmailMessage()
    msg['Subject'] = 'Tapin Password Reset'
    msg['From'] = smtp_user or f'no-reply@{smtp_host}'
    msg['To'] = to_email
    msg.set_content(f'Use the link to reset your password: {reset_url}')

    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True, 'sent'
    except Exception as e:
        return False, str(e)


@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({"error": "email required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        # Do not reveal whether the email exists
        return jsonify({"message": "If an account exists for that email, a reset link has been sent."})

    serializer = get_serializer()
    token = serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])
    reset_url = url_for('confirm_reset', token=token, _external=True)

    sent, info = send_reset_email(email, reset_url)
    if sent:
        return jsonify({"message": "reset email sent"})
    else:
        # Fallback in dev: return the reset_url so developers can use it
        return jsonify({"message": "smtp not configured, returning reset link (dev)", "reset_url": reset_url, "error": info})


@app.route('/reset-password/confirm/<token>', methods=['POST'])
def confirm_reset(token):
    data = request.get_json() or {}
    new_password = data.get('password')
    if not new_password:
        return jsonify({"error": "password required"}), 400
    serializer = get_serializer()
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
    except SignatureExpired:
        return jsonify({"error": "token expired"}), 400
    except BadSignature:
        return jsonify({"error": "invalid token"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "no such user"}), 404
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"message": "password updated"})


@app.route('/listings', methods=['GET'])
def get_listings():
    # Support simple filtering via query params: q (text search on title/description or category), location
    q = request.args.get('q', type=str)
    location = request.args.get('location', type=str)

    query = Listing.query
    if q:
        # Check if q matches a category exactly (case-insensitive)
        categories = ['Community', 'Environment', 'Education', 'Health', 'Animals']
        if q.lower() in [c.lower() for c in categories]:
            # Filter by category
            query = query.filter(Listing.category.ilike(q))
        else:
            # Text search on title/description
            like = f"%{q}%"
            query = query.filter((Listing.title.ilike(like)) | (Listing.description.ilike(like)))
    if location:
        query = query.filter(Listing.location.ilike(f"%{location}%"))

    listings = query.order_by(Listing.created_at.desc()).all()
    return jsonify([l.to_dict() for l in listings])


@app.route('/listings', methods=['POST'])
@jwt_required()
def create_listing():
    data = request.get_json() or {}
    title = data.get('title')
    if not title:
        return jsonify({"error": "title required"}), 400
    # JWT identity is stored as string; convert back to int for DB foreign key
    owner_id = int(get_jwt_identity())
    # Validate optional category
    category = data.get('category')
    allowed = ['Community', 'Environment', 'Education', 'Health', 'Animals']
    if category and category not in allowed:
        return jsonify({"error": "invalid category"}), 400

    # Parse optional coordinates
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    try:
        latitude = float(latitude) if latitude is not None else None
        longitude = float(longitude) if longitude is not None else None
    except (TypeError, ValueError):
        return jsonify({"error": "invalid coordinates"}), 400

    listing = Listing(
        title=title,
        description=data.get('description'),
        location=data.get('location'),
        latitude=latitude,
        longitude=longitude,
        category=category,
        image_url=data.get('image_url'),
        owner_id=owner_id,
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify(listing.to_dict()), 201


@app.route('/listings/<int:id>', methods=['GET'])
def get_listing_detail(id):
    listing = Listing.query.get_or_404(id)
    return jsonify(listing.to_dict())


@app.route('/listings/<int:id>', methods=['PUT'])
@jwt_required()
def update_listing(id):
    listing = Listing.query.get_or_404(id)
    # Verify ownership
    owner_id = int(get_jwt_identity())
    if listing.owner_id != owner_id:
        return jsonify({"error": "unauthorized - you don't own this listing"}), 403
    data = request.get_json() or {}
    listing.title = data.get('title', listing.title)
    listing.description = data.get('description', listing.description)
    listing.location = data.get('location', listing.location)
    # Optional fields
    if 'category' in data:
        category = data.get('category')
        allowed = ['Community', 'Environment', 'Education', 'Health', 'Animals']
        if category and category not in allowed:
            return jsonify({"error": "invalid category"}), 400
        listing.category = category
    if 'image_url' in data:
        listing.image_url = data.get('image_url')
    if 'latitude' in data or 'longitude' in data:
        try:
            if 'latitude' in data:
                listing.latitude = float(data.get('latitude')) if data.get('latitude') is not None else None
            if 'longitude' in data:
                listing.longitude = float(data.get('longitude')) if data.get('longitude') is not None else None
        except (TypeError, ValueError):
            return jsonify({"error": "invalid coordinates"}), 400
    db.session.commit()
    return jsonify(listing.to_dict())


@app.route('/listings/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_listing(id):
    listing = Listing.query.get_or_404(id)
    # Verify ownership
    owner_id = int(get_jwt_identity())
    if listing.owner_id != owner_id:
        return jsonify({"error": "unauthorized - you don't own this listing"}), 403
    db.session.delete(listing)
    db.session.commit()
    return jsonify({"message": "deleted"})


@app.route('/listings/<int:id>/signup', methods=['POST'])
@jwt_required()
def signup_for_listing(id):
    """Volunteer signs up for a listing."""
    listing = Listing.query.get_or_404(id)
    user_id = int(get_jwt_identity())
    
    # Check if already signed up
    existing = SignUp.query.filter_by(user_id=user_id, listing_id=id).first()
    if existing:
        return jsonify({"error": "already signed up for this listing"}), 400
    
    data = request.get_json() or {}
    signup = SignUp(
        user_id=user_id,
        listing_id=id,
        message=data.get('message'),
        status='pending'
    )
    db.session.add(signup)
    db.session.commit()
    
    return jsonify(signup.to_dict()), 201


@app.route('/listings/<int:id>/signups', methods=['GET'])
@jwt_required()
def get_listing_signups(id):
    """Get all sign-ups for a listing (owner only)."""
    listing = Listing.query.get_or_404(id)
    owner_id = int(get_jwt_identity())
    
    # Verify ownership
    if listing.owner_id != owner_id:
        return jsonify({"error": "unauthorized - you don't own this listing"}), 403
    
    signups = SignUp.query.filter_by(listing_id=id).order_by(SignUp.created_at.desc()).all()
    
    # Include user email with each sign-up
    results = []
    for signup in signups:
        signup_dict = signup.to_dict()
        user = db.session.get(User, signup.user_id)
        if user:
            signup_dict['user_email'] = user.email
        results.append(signup_dict)
    
    return jsonify(results)


@app.route('/signups/<int:id>', methods=['PUT'])
@jwt_required()
def update_signup_status(id):
    """Update sign-up status (owner can accept/decline, volunteer can cancel)."""
    signup = SignUp.query.get_or_404(id)
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({"error": "status required"}), 400
    
    # Get the listing to check ownership
    listing = db.session.get(Listing, signup.listing_id)
    if not listing:
        return jsonify({"error": "listing not found"}), 404
    
    # Owner can accept/decline, volunteer can cancel
    if listing.owner_id == user_id:
        if new_status not in ['accepted', 'declined']:
            return jsonify({"error": "owner can only set status to accepted or declined"}), 400
    elif signup.user_id == user_id:
        if new_status != 'cancelled':
            return jsonify({"error": "volunteer can only cancel sign-up"}), 400
    else:
        return jsonify({"error": "unauthorized"}), 403
    
    signup.status = new_status
    db.session.commit()
    return jsonify(signup.to_dict())


@app.route('/listings/<int:id>/reviews', methods=['POST'])
@jwt_required()
def create_review(id):
    """Create a review for a listing."""
    listing = Listing.query.get_or_404(id)
    user_id = int(get_jwt_identity())
    
    # Check if already reviewed
    existing = Review.query.filter_by(user_id=user_id, listing_id=id).first()
    if existing:
        return jsonify({"error": "you have already reviewed this listing"}), 400
    
    data = request.get_json() or {}
    rating = data.get('rating')
    
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "rating must be an integer between 1 and 5"}), 400
    
    review = Review(
        user_id=user_id,
        listing_id=id,
        rating=rating,
        comment=data.get('comment')
    )
    db.session.add(review)
    db.session.commit()
    
    return jsonify(review.to_dict()), 201


@app.route('/listings/<int:id>/reviews', methods=['GET'])
def get_listing_reviews(id):
    """Get all reviews for a listing."""
    listing = Listing.query.get_or_404(id)
    reviews = Review.query.filter_by(listing_id=id).order_by(Review.created_at.desc()).all()
    
    # Include user email with each review
    results = []
    for review in reviews:
        review_dict = review.to_dict()
        user = db.session.get(User, review.user_id)
        if user:
            review_dict['user_email'] = user.email
        results.append(review_dict)
    
    return jsonify(results)


@app.route('/listings/<int:id>/average-rating', methods=['GET'])
def get_listing_average_rating(id):
    """Get average rating for a listing."""
    listing = Listing.query.get_or_404(id)
    reviews = Review.query.filter_by(listing_id=id).all()

    if not reviews:
        return jsonify({"average_rating": 0, "review_count": 0})

    avg_rating = sum(r.rating for r in reviews) / len(reviews)
    return jsonify({
        "average_rating": round(avg_rating, 1),
        "review_count": len(reviews)
    })


@app.route('/api/events/eventbrite', methods=['GET'])
def get_eventbrite_events():
    """
    NOTE: Eventbrite deprecated their public events search API in 2020.
    This endpoint only works for events from your own organization.
    """
    return jsonify({
        "error": "Eventbrite public events search API was deprecated in 2020",
        "info": "The Eventbrite API only allows access to your own organization's events",
        "alternative": "Use the Ticketmaster API for public event search",
        "documentation": "https://www.eventbrite.com/platform/docs"
    }), 501


@app.route('/api/events/ticketmaster', methods=['GET'])
def get_ticketmaster_events():
    """Fetch public events from Ticketmaster Discovery API."""
    tm_key = os.environ.get('TICKETMASTER_API_KEY')
    if not tm_key:
        return jsonify({"error": "Ticketmaster API key not configured"}), 500

    url = "https://app.ticketmaster.com/discovery/v2/events"
    city = request.args.get("city", "Houston")
    state_code = request.args.get("state", "TX")
    params = {
        "apikey": tm_key,
        "city": city,
        "stateCode": state_code,
        "countryCode": request.args.get("country", "US"),
        "classificationName": request.args.get("category"),
        "keyword": request.args.get("q"),
        "size": request.args.get("size", 20),
        "page": request.args.get("page", 0),
        "sort": "date,asc",
    }
    params = {k: v for k, v in params.items() if v}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        events = []
        for e in data.get("_embedded", {}).get("events", []):
            venue_info = e.get("_embedded", {}).get("venues", [{}])[0]
            events.append({
                "id": e.get("id"),
                "source": "ticketmaster",
                "name": e.get("name"),
                "description": e.get("info", ""),
                "start": e.get("dates", {}).get("start", {}).get("localDate"),
                "start_time": e.get("dates", {}).get("start", {}).get("localTime"),
                "url": e.get("url"),
                "venue": venue_info.get("name"),
                "venue_address": venue_info.get("address", {}).get("line1"),
                "image": e.get("images", [{}])[0].get("url") if e.get("images") else None,
            })
        return jsonify({
            "events": events,
            "pagination": data.get("page", {}),
            "total": data.get("page", {}).get("totalElements", 0)
        })
    except Exception as ex:
        return jsonify({"error": str(ex), "source": "ticketmaster"}), 502


@app.route('/api/events/seatgeek', methods=['GET'])
def get_seatgeek_events():
    """Fetch public events from SeatGeek API."""
    client_id = os.environ.get('SEATGEEK_CLIENT_ID')
    if not client_id:
        return jsonify({"error": "SeatGeek client_id not configured"}), 500

    url = "https://api.seatgeek.com/2/events"
    params = {
        "client_id": client_id,
        "venue.city": request.args.get("city", "Houston"),
        "venue.state": request.args.get("state", "TX"),
        "type": request.args.get("category"),  # concert, sports, theater, etc.
        "q": request.args.get("q"),  # search query
        "per_page": request.args.get("size", 25),
        "page": request.args.get("page", 1),
        "sort": "datetime_utc.asc",
    }
    params = {k: v for k, v in params.items() if v}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        events = []

        for e in data.get("events", []):
            venue = e.get("venue", {})
            events.append({
                "id": e.get("id"),
                "source": "seatgeek",
                "name": e.get("title"),
                "description": e.get("description"),
                "start": e.get("datetime_local"),
                "url": e.get("url"),
                "venue": venue.get("name"),
                "venue_address": f"{venue.get('address', '')}, {venue.get('city', '')}, {venue.get('state', '')}".strip(", "),
                "image": e.get("performers", [{}])[0].get("image") if e.get("performers") else None,
                "type": e.get("type"),
                "score": e.get("score"),  # SeatGeek popularity score
            })

        return jsonify({
            "events": events,
            "pagination": {
                "page": data.get("meta", {}).get("page"),
                "per_page": data.get("meta", {}).get("per_page"),
                "total": data.get("meta", {}).get("total")
            },
            "total": data.get("meta", {}).get("total", 0)
        })
    except Exception as ex:
        return jsonify({"error": str(ex), "source": "seatgeek"}), 502


@app.route('/api/events/all', methods=['GET'])
def get_all_events():
    """Aggregate events from all configured sources (Ticketmaster + SeatGeek)."""
    from datetime import datetime as dt
    all_events = []
    errors = []
    city = request.args.get("city", "Houston")
    state = request.args.get("state", "TX")

    # Get current datetime for filtering
    now = dt.now()

    # Try Ticketmaster
    tm_key = os.environ.get('TICKETMASTER_API_KEY')
    if tm_key:
        try:
            tm_url = "https://app.ticketmaster.com/discovery/v2/events"
            tm_params = {
                "apikey": tm_key,
                "city": city,
                "stateCode": state,
                "size": 25,
                "sort": "date,asc",
            }
            resp = requests.get(tm_url, params=tm_params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for e in data.get("_embedded", {}).get("events", []):
                venue_info = e.get("_embedded", {}).get("venues", [{}])[0]
                event_date = e.get("dates", {}).get("start", {}).get("localDate")

                # Skip past events
                if event_date:
                    try:
                        event_datetime = dt.fromisoformat(event_date)
                        if event_datetime.date() < now.date():
                            continue
                    except (ValueError, AttributeError):
                        pass  # Include event if date parsing fails

                all_events.append({
                    "id": f"tm_{e.get('id')}",
                    "source": "ticketmaster",
                    "name": e.get("name"),
                    "start": event_date,
                    "start_time": e.get("dates", {}).get("start", {}).get("localTime"),
                    "url": e.get("url"),
                    "venue": venue_info.get("name"),
                    "image": e.get("images", [{}])[0].get("url") if e.get("images") else None,
                })
        except Exception as ex:
            errors.append({"source": "ticketmaster", "error": str(ex)})

    # Try SeatGeek
    sg_client_id = os.environ.get('SEATGEEK_CLIENT_ID')
    if sg_client_id:
        try:
            sg_url = "https://api.seatgeek.com/2/events"
            sg_params = {
                "client_id": sg_client_id,
                "venue.city": city,
                "venue.state": state,
                "per_page": 25,
                "sort": "datetime_utc.asc",
            }
            resp = requests.get(sg_url, params=sg_params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for e in data.get("events", []):
                venue = e.get("venue", {})
                event_datetime_str = e.get("datetime_local")

                # Skip past events
                if event_datetime_str:
                    try:
                        event_datetime = dt.fromisoformat(event_datetime_str.replace('Z', '+00:00'))
                        if event_datetime < now:
                            continue
                    except (ValueError, AttributeError):
                        pass  # Include event if date parsing fails

                all_events.append({
                    "id": f"sg_{e.get('id')}",
                    "source": "seatgeek",
                    "name": e.get("title"),
                    "start": event_datetime_str,
                    "url": e.get("url"),
                    "venue": venue.get("name"),
                    "image": e.get("performers", [{}])[0].get("image") if e.get("performers") else None,
                })
        except Exception as ex:
            errors.append({"source": "seatgeek", "error": str(ex)})

    # Sort all events by start date
    all_events.sort(key=lambda x: x.get("start", ""), reverse=False)

    sources = []
    if tm_key:
        sources.append("ticketmaster")
    if sg_client_id:
        sources.append("seatgeek")

    return jsonify({
        "events": all_events,
        "total": len(all_events),
        "errors": errors if errors else None,
        "sources_queried": sources,
        "note": "Showing upcoming events only"
    })


@app.route('/api/events/community', methods=['GET'])
def get_community_events():
    """Fetch community events using SerpApi Google Search."""
    serpapi_key = os.environ.get('SERPAPI_KEY')
    if not serpapi_key:
        return jsonify({"error": "SerpApi key not configured"}), 500

    try:
        from datetime import datetime as dt

        city = request.args.get("city", "Houston")
        state = request.args.get("state", "TX")

        # Search for community events using Google
        url = "https://serpapi.com/search.json"

        params = {
            "engine": "google",
            "q": f"community events {city} {state}",
            "location": f"{city}, {state}, United States",
            "tbm": "nws",  # News search for events
            "api_key": serpapi_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        events = []
        now = dt.now()

        # Parse news results for events
        for item in data.get("news_results", [])[:20]:
            # Extract date if available
            date_str = item.get("date", "")

            events.append({
                "id": f"serp_{hash(item.get('link', ''))}",
                "source": "community",
                "name": item.get("title"),
                "start": date_str,
                "url": item.get("link"),
                "venue": f"{city}, {state}",
                "description": item.get("snippet", "")[:200],
                "image": item.get("thumbnail"),
                "category": "community"
            })

        return jsonify({
            "events": events,
            "total": len(events),
            "source": "serpapi",
            "note": "Community events powered by Google Search"
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"SerpApi error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error processing community events: {str(e)}"}), 500


@app.route('/api/agent/populate-listings', methods=['POST'])
def populate_listings_from_events():
    """AI agent to auto-populate listings from event APIs for future events only."""
    try:
        from datetime import datetime as dt

        # Category mapping: event categories to listing categories
        category_map = {
            'music': 'Community',
            'sports': 'Community',
            'arts': 'Community',
            'theater': 'Community',
            'family': 'Community',
            'community': 'Community'
        }

        # Get all future events from Ticketmaster
        tm_key = os.environ.get('TICKETMASTER_API_KEY')
        sg_client_id = os.environ.get('SEATGEEK_CLIENT_ID')

        created_listings = []
        skipped_events = []
        now = dt.now()

        # Fetch from Ticketmaster (multiple categories)
        if tm_key:
            for event_category in ['music', 'sports', 'arts', 'family']:
                try:
                    url = "https://app.ticketmaster.com/discovery/v2/events"
                    params = {
                        "apikey": tm_key,
                        "city": "Houston",
                        "stateCode": "TX",
                        "classificationName": event_category,
                        "size": 10,
                        "sort": "date,asc"
                    }

                    response = requests.get(url, params=params, timeout=10)
                    if response.ok:
                        data = response.json()
                        events = data.get("_embedded", {}).get("events", [])

                        for e in events:
                            # Parse event date
                            start_date_str = e.get("dates", {}).get("start", {}).get("dateTime") or e.get("dates", {}).get("start", {}).get("localDate")
                            if not start_date_str:
                                continue

                            # Skip past events
                            try:
                                event_date = dt.fromisoformat(start_date_str.replace('Z', '+00:00'))
                                if event_date.date() < now.date():
                                    skipped_events.append(e.get("name"))
                                    continue
                            except:
                                pass  # Include if date parsing fails

                            # Check if listing already exists
                            event_url = e.get("url", "")
                            existing = Listing.query.filter_by(description=f"Event URL: {event_url}").first()
                            if existing:
                                continue

                            # Extract venue info
                            venue = e.get("_embedded", {}).get("venues", [{}])[0]
                            venue_name = venue.get("name", "Houston, TX")
                            lat = venue.get("location", {}).get("latitude")
                            lon = venue.get("location", {}).get("longitude")

                            # Create listing from event
                            listing = Listing(
                                title=e.get("name", "Event")[:200],
                                description=f"Event URL: {event_url}\n\nDate: {start_date_str}\n\nJoin this {event_category} event in Houston!",
                                location=venue_name,
                                latitude=float(lat) if lat else None,
                                longitude=float(lon) if lon else None,
                                category=category_map.get(event_category, 'Community'),
                                image_url=e.get("images", [{}])[0].get("url") if e.get("images") else None,
                                owner_id=None  # System-generated listing
                            )

                            db.session.add(listing)
                            created_listings.append(listing.title)

                except Exception as ex:
                    print(f"Error fetching {event_category} events: {ex}")
                    continue

        # Commit all new listings
        db.session.commit()

        return jsonify({
            "success": True,
            "created": len(created_listings),
            "skipped_past_events": len(skipped_events),
            "sample_created": created_listings[:5],
            "message": f"Successfully created {len(created_listings)} listings from future events"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Agent error: {str(e)}"}), 500


@app.route('/api/agent/ai-populate', methods=['POST'])
def ai_populate_listings():
    """AI-powered agent using Gemini to intelligently populate categories with image-rich events."""
    try:
        import google.generativeai as genai
        from datetime import datetime as dt

        gemini_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_key:
            return jsonify({"error": "Gemini API key not configured"}), 500

        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Analyze current listings by category
        all_listings = Listing.query.all()
        category_counts = {}
        for listing in all_listings:
            cat = listing.category or 'Uncategorized'
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Ask Gemini which categories need more events
        prompt = f"""Analyze these event category counts and suggest which 3 categories need more diversity:
Categories: {category_counts}

Available event types: music concerts, sports games, theater shows, art exhibitions, family activities, community gatherings.

Respond with ONLY a JSON array of 3 category names to prioritize, like: ["music", "sports", "family"]"""

        response = model.generate_content(prompt)
        import json
        try:
            priority_categories = json.loads(response.text.strip())
        except:
            # Fallback if AI doesn't return valid JSON
            priority_categories = ["music", "sports", "family"]

        # Fetch events from priority categories (only with images)
        tm_key = os.environ.get('TICKETMASTER_API_KEY')
        created_listings = []
        now = dt.now()

        if tm_key:
            for event_category in priority_categories[:3]:  # Top 3 priorities
                try:
                    url = "https://app.ticketmaster.com/discovery/v2/events"
                    params = {
                        "apikey": tm_key,
                        "city": "Houston",
                        "stateCode": "TX",
                        "classificationName": event_category,
                        "size": 15,
                        "sort": "date,asc"
                    }

                    response_events = requests.get(url, params=params, timeout=10)
                    if response_events.ok:
                        data = response_events.json()
                        events = data.get("_embedded", {}).get("events", [])

                        for e in events:
                            # ONLY process events with images
                            if not e.get("images"):
                                continue

                            # Skip past events
                            start_date_str = e.get("dates", {}).get("start", {}).get("dateTime") or e.get("dates", {}).get("start", {}).get("localDate")
                            if start_date_str:
                                try:
                                    event_date = dt.fromisoformat(start_date_str.replace('Z', '+00:00'))
                                    if event_date.date() < now.date():
                                        continue
                                except:
                                    pass

                            # Check if already exists
                            event_url = e.get("url", "")
                            existing = Listing.query.filter_by(description=f"Event URL: {event_url}").first()
                            if existing:
                                continue

                            # Use Gemini to generate engaging description
                            event_name = e.get("name", "Event")
                            desc_prompt = f"Write a short, engaging 2-sentence description for this event: {event_name}. Make it exciting and community-focused."

                            try:
                                desc_response = model.generate_content(desc_prompt)
                                ai_description = desc_response.text.strip()
                            except:
                                ai_description = f"Join this {event_category} event in Houston!"

                            # Extract venue
                            venue = e.get("_embedded", {}).get("venues", [{}])[0]
                            venue_name = venue.get("name", "Houston, TX")
                            lat = venue.get("location", {}).get("latitude")
                            lon = venue.get("location", {}).get("longitude")

                            # Get best quality image
                            images = e.get("images", [])
                            best_image = max(images, key=lambda img: img.get("width", 0) * img.get("height", 0))

                            listing = Listing(
                                title=event_name[:200],
                                description=f"{ai_description}\n\nEvent URL: {event_url}\nDate: {start_date_str}",
                                location=venue_name,
                                latitude=float(lat) if lat else None,
                                longitude=float(lon) if lon else None,
                                category="Community",
                                image_url=best_image.get("url"),
                                owner_id=None
                            )

                            db.session.add(listing)
                            created_listings.append(listing.title)

                            # Limit to 5 per category
                            if len([l for l in created_listings if event_category in l.lower()]) >= 5:
                                break

                except Exception as ex:
                    print(f"Error in AI agent for {event_category}: {ex}")
                    continue

        db.session.commit()

        return jsonify({
            "success": True,
            "ai_analysis": {
                "current_counts": category_counts,
                "prioritized": priority_categories
            },
            "created": len(created_listings),
            "listings": created_listings[:10],
            "message": f"AI agent created {len(created_listings)} image-rich listings in priority categories"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"AI Agent error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
