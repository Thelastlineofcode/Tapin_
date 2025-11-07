"""
Tests for Sign-up and Review features (Sprint 1)
Tests Stories 1.1 and 1.4
"""
import pytest
from app import app, db, User, Listing, SignUp, Review
from auth import token_for
from werkzeug.security import generate_password_hash


@pytest.fixture
def create_listing(create_user):
    """Create a test listing owned by a user"""
    def _create_listing(title="Test Listing", owner_id=None):
        if owner_id is None:
            owner_id = create_user(email="owner@test.com")
        
        with app.app_context():
            listing = Listing(
                title=title,
                description="Test description",
                location="Test location",
                owner_id=owner_id
            )
            db.session.add(listing)
            db.session.commit()
            return listing.id
    return _create_listing


class TestSignUpFeature:
    """Tests for Story 1.1: Sign-up/Connect to Listings"""
    
    def test_sign_up_to_listing_success(self, client, create_user, create_listing):
        """Test volunteer can sign up for a listing"""
        owner_id = create_user(email="owner@test.com")
        volunteer_id = create_user(email="volunteer@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        token = token_for(volunteer_id)
        headers = {"Authorization": f"Bearer {token}"}
        
        resp = client.post(
            f"/listings/{listing_id}/signup",
            json={"message": "I'd love to help!"},
            headers=headers
        )
        
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["status"] == "pending"
        assert data["message"] == "I'd love to help!"
        assert "id" in data
    
    def test_sign_up_requires_authentication(self, client, create_listing):
        """Test sign-up requires JWT token"""
        listing_id = create_listing()
        
        resp = client.post(
            f"/listings/{listing_id}/signup",
            json={"message": "Test"}
        )
        
        assert resp.status_code == 401
    
    def test_sign_up_duplicate_prevention(self, client, create_user, create_listing):
        """Test user cannot sign up twice for same listing"""
        owner_id = create_user(email="owner@test.com")
        volunteer_id = create_user(email="volunteer@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        token = token_for(volunteer_id)
        headers = {"Authorization": f"Bearer {token}"}
        
        # First sign-up
        resp1 = client.post(
            f"/listings/{listing_id}/signup",
            json={"message": "First"},
            headers=headers
        )
        assert resp1.status_code == 201
        
        # Second sign-up (should fail)
        resp2 = client.post(
            f"/listings/{listing_id}/signup",
            json={"message": "Second"},
            headers=headers
        )
        assert resp2.status_code == 400
        assert "already signed up" in resp2.get_json()["error"].lower()
    
    def test_sign_up_optional_message(self, client, create_user, create_listing):
        """Test sign-up works without message"""
        owner_id = create_user(email="owner@test.com")
        volunteer_id = create_user(email="volunteer@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        token = token_for(volunteer_id)
        headers = {"Authorization": f"Bearer {token}"}
        
        resp = client.post(
            f"/listings/{listing_id}/signup",
            json={},
            headers=headers
        )
        
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["message"] is None or data["message"] == ""
    
    def test_get_listing_signups_owner_only(self, client, create_user, create_listing):
        """Test only listing owner can view sign-ups"""
        owner_id = create_user(email="owner@test.com")
        volunteer_id = create_user(email="volunteer@test.com")
        other_user_id = create_user(email="other@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        # Create a sign-up
        volunteer_token = token_for(volunteer_id)
        client.post(
            f"/listings/{listing_id}/signup",
            json={"message": "Test"},
            headers={"Authorization": f"Bearer {volunteer_token}"}
        )
        
        # Owner should see sign-ups
        owner_token = token_for(owner_id)
        resp_owner = client.get(
            f"/listings/{listing_id}/signups",
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        assert resp_owner.status_code == 200
        data = resp_owner.get_json()
        assert len(data["signups"]) == 1
        assert "user_email" in data["signups"][0]
        
        # Other user should not see sign-ups
        other_token = token_for(other_user_id)
        resp_other = client.get(
            f"/listings/{listing_id}/signups",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        assert resp_other.status_code == 403
    
    def test_update_signup_status_owner(self, client, create_user, create_listing):
        """Test owner can accept/decline sign-ups"""
        owner_id = create_user(email="owner@test.com")
        volunteer_id = create_user(email="volunteer@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        # Create sign-up
        volunteer_token = token_for(volunteer_id)
        resp_signup = client.post(
            f"/listings/{listing_id}/signup",
            json={"message": "Test"},
            headers={"Authorization": f"Bearer {volunteer_token}"}
        )
        signup_id = resp_signup.get_json()["id"]
        
        # Owner accepts
        owner_token = token_for(owner_id)
        resp = client.put(
            f"/signups/{signup_id}",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "accepted"
    
    def test_update_signup_status_volunteer_cancel(self, client, create_user, create_listing):
        """Test volunteer can cancel their own sign-up"""
        owner_id = create_user(email="owner@test.com")
        volunteer_id = create_user(email="volunteer@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        # Create sign-up
        volunteer_token = token_for(volunteer_id)
        resp_signup = client.post(
            f"/listings/{listing_id}/signup",
            json={"message": "Test"},
            headers={"Authorization": f"Bearer {volunteer_token}"}
        )
        signup_id = resp_signup.get_json()["id"]
        
        # Volunteer cancels
        resp = client.put(
            f"/signups/{signup_id}",
            json={"status": "cancelled"},
            headers={"Authorization": f"Bearer {volunteer_token}"}
        )
        
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "cancelled"


class TestReviewFeature:
    """Tests for Story 1.4: Reviews and Ratings"""
    
    def test_create_review_success(self, client, create_user, create_listing):
        """Test user can create a review"""
        owner_id = create_user(email="owner@test.com")
        reviewer_id = create_user(email="reviewer@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        token = token_for(reviewer_id)
        headers = {"Authorization": f"Bearer {token}"}
        
        resp = client.post(
            f"/listings/{listing_id}/reviews",
            json={"rating": 5, "comment": "Great experience!"},
            headers=headers
        )
        
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["rating"] == 5
        assert data["comment"] == "Great experience!"
        assert "id" in data
    
    def test_create_review_requires_authentication(self, client, create_listing):
        """Test review creation requires JWT token"""
        listing_id = create_listing()
        
        resp = client.post(
            f"/listings/{listing_id}/reviews",
            json={"rating": 5, "comment": "Test"}
        )
        
        assert resp.status_code == 401
    
    def test_review_rating_validation(self, client, create_user, create_listing):
        """Test rating must be between 1-5"""
        owner_id = create_user(email="owner@test.com")
        reviewer_id = create_user(email="reviewer@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        token = token_for(reviewer_id)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test rating too low
        resp_low = client.post(
            f"/listings/{listing_id}/reviews",
            json={"rating": 0, "comment": "Bad"},
            headers=headers
        )
        assert resp_low.status_code == 400
        
        # Test rating too high
        resp_high = client.post(
            f"/listings/{listing_id}/reviews",
            json={"rating": 6, "comment": "Good"},
            headers=headers
        )
        assert resp_high.status_code == 400
        
        # Test valid rating
        resp_valid = client.post(
            f"/listings/{listing_id}/reviews",
            json={"rating": 3, "comment": "OK"},
            headers=headers
        )
        assert resp_valid.status_code == 201
    
    def test_review_duplicate_prevention(self, client, create_user, create_listing):
        """Test user cannot review same listing twice"""
        owner_id = create_user(email="owner@test.com")
        reviewer_id = create_user(email="reviewer@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        token = token_for(reviewer_id)
        headers = {"Authorization": f"Bearer {token}"}
        
        # First review
        resp1 = client.post(
            f"/listings/{listing_id}/reviews",
            json={"rating": 5, "comment": "First"},
            headers=headers
        )
        assert resp1.status_code == 201
        
        # Second review (should fail)
        resp2 = client.post(
            f"/listings/{listing_id}/reviews",
            json={"rating": 4, "comment": "Second"},
            headers=headers
        )
        assert resp2.status_code == 400
        assert "already reviewed" in resp2.get_json()["error"].lower()
    
    def test_review_optional_comment(self, client, create_user, create_listing):
        """Test review works with just rating, no comment"""
        owner_id = create_user(email="owner@test.com")
        reviewer_id = create_user(email="reviewer@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        token = token_for(reviewer_id)
        headers = {"Authorization": f"Bearer {token}"}
        
        resp = client.post(
            f"/listings/{listing_id}/reviews",
            json={"rating": 4},
            headers=headers
        )
        
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["rating"] == 4
        assert data["comment"] is None or data["comment"] == ""
    
    def test_get_listing_reviews(self, client, create_user, create_listing):
        """Test anyone can view reviews (public endpoint)"""
        owner_id = create_user(email="owner@test.com")
        reviewer_id = create_user(email="reviewer@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        # Create a review
        token = token_for(reviewer_id)
        client.post(
            f"/listings/{listing_id}/reviews",
            json={"rating": 5, "comment": "Great!"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Get reviews (no auth needed)
        resp = client.get(f"/listings/{listing_id}/reviews")
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["reviews"]) == 1
        assert data["reviews"][0]["rating"] == 5
        assert "user_email" in data["reviews"][0]
    
    def test_get_average_rating(self, client, create_user, create_listing):
        """Test average rating calculation"""
        owner_id = create_user(email="owner@test.com")
        listing_id = create_listing(owner_id=owner_id)
        
        # Create multiple reviews
        for i, rating in enumerate([5, 4, 3], 1):
            reviewer_id = create_user(email=f"reviewer{i}@test.com")
            token = token_for(reviewer_id)
            client.post(
                f"/listings/{listing_id}/reviews",
                json={"rating": rating},
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Get average
        resp = client.get(f"/listings/{listing_id}/average-rating")
        
        assert resp.status_code == 200
        data = resp.get_json()
        # Average of 5, 4, 3 = 4.0
        assert data["average_rating"] == 4.0
        assert data["review_count"] == 3
    
    def test_average_rating_no_reviews(self, client, create_listing):
        """Test average rating when no reviews exist"""
        listing_id = create_listing()
        
        resp = client.get(f"/listings/{listing_id}/average-rating")
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["average_rating"] is None
        assert data["review_count"] == 0
