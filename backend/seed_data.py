"""
Seed script to populate the database with sample data for UI testing
Run with: python backend/seed_data.py
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import app, db, User, Listing, Item, SignUp, Review
from werkzeug.security import generate_password_hash

def clear_database():
    """Clear all data from the database"""
    print("🗑️  Clearing existing data...")
    with app.app_context():
        Review.query.delete()
        SignUp.query.delete()
        Item.query.delete()
        Listing.query.delete()
        User.query.delete()
        db.session.commit()
    print("✓ Database cleared")

def create_sample_users():
    """Create sample users"""
    print("\n👥 Creating sample users...")
    
    users_data = [
        {
            'email': 'volunteer1@example.com',
            'password': 'password123',
            'role': 'user'
        },
        {
            'email': 'volunteer2@example.com',
            'password': 'password123',
            'role': 'user'
        },
        {
            'email': 'volunteer3@example.com',
            'password': 'password123',
            'role': 'user'
        },
        {
            'email': 'org1@example.com',
            'password': 'password123',
            'role': 'user'
        },
        {
            'email': 'org2@example.com',
            'password': 'password123',
            'role': 'user'
        },
        {
            'email': 'org3@example.com',
            'password': 'password123',
            'role': 'user'
        },
    ]
    
    users = []
    with app.app_context():
        for data in users_data:
            user = User(
                email=data['email'],
                password_hash=generate_password_hash(data['password']),
                role=data['role']
            )
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        # Refresh to get IDs
        for user in users:
            db.session.refresh(user)
        print(f"✓ Created {len(users)} users")
        return [u.id for u in users]

def create_sample_listings(user_ids):
    """Create sample volunteer opportunity listings"""
    print("\n📋 Creating sample listings...")
    
    listings_data = [
        {
            'title': 'Community Beach Cleanup',
            'description': 'Join us for a morning beach cleanup! Help keep our shores clean and protect marine life. All supplies provided. Perfect for individuals, families, and groups. No experience necessary.',
            'location': 'Santa Monica Beach, CA',
            'latitude': 34.0195,
            'longitude': -118.4912,
            'category': 'Environment',
            'image_url': 'https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?w=800&h=600&fit=crop',
        },
        {
            'title': 'Food Bank Volunteer',
            'description': 'Help sort and distribute food to families in need. Morning and afternoon shifts available. Great opportunity to give back to your local community. Training provided on-site.',
            'location': 'Downtown LA Food Bank',
            'latitude': 34.0407,
            'longitude': -118.2468,
            'category': 'Community',
            'image_url': 'https://images.unsplash.com/photo-1593113598332-cd288d649433?w=800&h=600&fit=crop',
        },
        {
            'title': 'Senior Center Activities Helper',
            'description': 'Assist with recreational activities at our senior center. Help organize game nights, craft sessions, and social events. Bring joy to our elderly community members. Patient and friendly volunteers welcome.',
            'location': 'Pasadena Senior Center',
            'latitude': 34.1478,
            'longitude': -118.1445,
            'category': 'Health',
            'image_url': 'https://images.unsplash.com/photo-1581579438747-1dc8d17bbce4?w=800&h=600&fit=crop',
        },
        {
            'title': 'Animal Shelter Dog Walker',
            'description': 'Love dogs? Help socialize our shelter dogs by taking them for walks. Must be comfortable with dogs of all sizes. Orientation required. Flexible schedule - even 1 hour helps!',
            'location': 'LA County Animal Shelter',
            'latitude': 34.2081,
            'longitude': -118.1708,
            'category': 'Animals',
            'image_url': 'https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=800&h=600&fit=crop',
        },
        {
            'title': 'Youth Tutoring Program',
            'description': 'Tutor middle and high school students in math, science, or English. Make a lasting impact on a young person\'s education. 2-3 hours per week commitment. Virtual or in-person options.',
            'location': 'Inglewood Community Center',
            'latitude': 33.9617,
            'longitude': -118.3531,
            'category': 'Education',
            'image_url': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=800&h=600&fit=crop',
        },
        {
            'title': 'Community Garden Maintenance',
            'description': 'Help maintain our thriving community garden! Plant, water, weed, and harvest fresh produce. Learn sustainable gardening practices. All produce shared with local families and volunteers.',
            'location': 'Venice Community Garden',
            'latitude': 33.9850,
            'longitude': -118.4695,
            'category': 'Environment',
            'image_url': 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800&h=600&fit=crop',
        },
        {
            'title': 'Homeless Outreach Team',
            'description': 'Join our street outreach team to distribute meals, hygiene kits, and connect people with resources. Training and supervision provided. Must be 18+ and compassionate.',
            'location': 'Skid Row, Downtown LA',
            'latitude': 34.0443,
            'longitude': -118.2420,
            'category': 'Community',
            'image_url': 'https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?w=800&h=600&fit=crop',
        },
        {
            'title': 'Hospital Visit Program',
            'description': 'Bring comfort to hospital patients through friendly visits and conversation. Background check required. Weekday and weekend opportunities. Meaningful connections that brighten someone\'s day.',
            'location': 'Cedars-Sinai Medical Center',
            'latitude': 34.0754,
            'longitude': -118.3776,
            'category': 'Health',
            'image_url': 'https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800&h=600&fit=crop',
        },
        {
            'title': 'Trail Restoration Project',
            'description': 'Help restore hiking trails in Griffith Park. Remove invasive plants, repair erosion, and plant native species. Outdoor work, good exercise, and beautiful views. Tools provided.',
            'location': 'Griffith Park',
            'latitude': 34.1341,
            'longitude': -118.2942,
            'category': 'Environment',
            'image_url': 'https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&h=600&fit=crop',
        },
        {
            'title': 'Literacy Program Reading Buddy',
            'description': 'Read with elementary students to improve their literacy skills. One-on-one or small group sessions. Patient and encouraging volunteers needed. See the joy of reading come alive!',
            'location': 'Long Beach Library',
            'latitude': 33.7701,
            'longitude': -118.1937,
            'category': 'Education',
            'image_url': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&h=600&fit=crop',
        },
        {
            'title': 'Habitat for Humanity Build Day',
            'description': 'Help build affordable housing for families in need. No construction experience required - we\'ll teach you! Bring work gloves and closed-toe shoes. Ages 16+ welcome with adult.',
            'location': 'Culver City Build Site',
            'latitude': 34.0211,
            'longitude': -118.3965,
            'category': 'Community',
            'image_url': 'https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?w=800&h=600&fit=crop',
        },
        {
            'title': 'Museum Tour Guide',
            'description': 'Share your passion for art and history as a volunteer tour guide. Training program provided. Flexible schedule, minimum 2 tours per month. Great public speaking opportunity.',
            'location': 'Getty Center',
            'latitude': 34.0780,
            'longitude': -118.4741,
            'category': 'Education',
            'image_url': 'https://images.unsplash.com/photo-1554907984-15263bfd63bd?w=800&h=600&fit=crop',
        },
        {
            'title': 'Pet Shelter Adoption Events',
            'description': 'Help facilitate pet adoption events! Assist potential adopters, answer questions about our animals, and help with event setup/cleanup. Must love animals and people equally!',
            'location': 'West LA Animal Shelter',
            'latitude': 34.0522,
            'longitude': -118.4437,
            'category': 'Animals',
            'image_url': 'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=800&h=600&fit=crop',
        },
        {
            'title': 'Meal Delivery for Homebound Seniors',
            'description': 'Deliver hot, nutritious meals to seniors who cannot leave their homes. Brief friendly visits brighten their day. Flexible morning schedule, reliable transportation required.',
            'location': 'Santa Monica Meals on Wheels',
            'latitude': 34.0194,
            'longitude': -118.4912,
            'category': 'Health',
            'image_url': 'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=800&h=600&fit=crop',
        },
        {
            'title': 'Wildlife Rescue Assistant',
            'description': 'Support our wildlife rehabilitation center. Help prepare food for animals, clean enclosures, and assist with release preparations. Training provided. Nature lovers welcome!',
            'location': 'Malibu Canyon Wildlife Center',
            'latitude': 34.0369,
            'longitude': -118.7004,
            'category': 'Animals',
            'image_url': 'https://images.unsplash.com/photo-1425082661705-1834bfd09dca?w=800&h=600&fit=crop',
        },
    ]
    
    listings = []
    with app.app_context():
        for i, data in enumerate(listings_data):
            listing = Listing(
                title=data['title'],
                description=data['description'],
                location=data['location'],
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                category=data.get('category'),
                image_url=data.get('image_url'),
                owner_id=user_ids[i % len(user_ids)]  # Distribute among users
            )
            db.session.add(listing)
            listings.append(listing)
        
        db.session.commit()
        print(f"✓ Created {len(listings)} listings")
        return [l.id for l in listings]

def create_sample_signups(user_ids, listing_ids):
    """Create sample volunteer sign-ups"""
    print("\n✋ Creating sample sign-ups...")
    
    signups = []
    used_pairs = set()
    
    with app.app_context():
        # Create some accepted sign-ups
        for i in range(8):
            user_idx = i % len(user_ids)
            listing_idx = (i + 3) % len(listing_ids)  # Offset to avoid conflicts
            pair = (user_ids[user_idx], listing_ids[listing_idx])
            
            if pair not in used_pairs:
                used_pairs.add(pair)
                signup = SignUp(
                    user_id=pair[0],
                    listing_id=pair[1],
                    message=f"I'd love to volunteer! I have experience with similar activities.",
                    status='accepted'
                )
                db.session.add(signup)
                signups.append(signup)
        
        # Create some pending sign-ups
        for i in range(5):
            user_idx = (i + 2) % len(user_ids)
            listing_idx = (i * 2) % len(listing_ids)  # Different offset
            pair = (user_ids[user_idx], listing_ids[listing_idx])
            
            if pair not in used_pairs:
                used_pairs.add(pair)
                signup = SignUp(
                    user_id=pair[0],
                    listing_id=pair[1],
                    message=f"Count me in! What should I bring?",
                    status='pending'
                )
                db.session.add(signup)
                signups.append(signup)
        
        db.session.commit()
        print(f"✓ Created {len(signups)} sign-ups")

def create_sample_reviews(user_ids, listing_ids):
    """Create sample reviews"""
    print("\n⭐ Creating sample reviews...")
    
    reviews_data = [
        {'rating': 5, 'comment': 'Amazing experience! The organizers were so welcoming and everything was well-planned.'},
        {'rating': 5, 'comment': 'Loved volunteering here. Made a real difference and met great people!'},
        {'rating': 4, 'comment': 'Great opportunity! Very fulfilling. Would have liked clearer instructions at the start.'},
        {'rating': 5, 'comment': 'Highly recommend! Perfect for first-time volunteers.'},
        {'rating': 4, 'comment': 'Good experience overall. Looking forward to volunteering again next month.'},
        {'rating': 5, 'comment': 'The best volunteer experience I\'ve had. Staff was incredibly supportive.'},
        {'rating': 3, 'comment': 'Decent opportunity but a bit disorganized. Still glad I participated.'},
        {'rating': 5, 'comment': 'Wonderful cause and wonderful people. Can\'t wait to come back!'},
        {'rating': 4, 'comment': 'Really enjoyed it! Great way to spend a Saturday morning.'},
        {'rating': 5, 'comment': 'Exceeded my expectations. Very professionally run and impactful work.'},
    ]
    
    reviews = []
    with app.app_context():
        for i, data in enumerate(reviews_data):
            # Only create reviews where the user has signed up (simulating completed volunteering)
            review = Review(
                user_id=user_ids[i % len(user_ids)],
                listing_id=listing_ids[i % len(listing_ids)],
                rating=data['rating'],
                comment=data['comment']
            )
            db.session.add(review)
            reviews.append(review)
        
        db.session.commit()
        print(f"✓ Created {len(reviews)} reviews")

def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    print("=" * 50)
    
    # Clear existing data
    clear_database()
    
    # Create sample data
    user_ids = create_sample_users()
    listing_ids = create_sample_listings(user_ids)
    create_sample_signups(user_ids, listing_ids)
    create_sample_reviews(user_ids, listing_ids)
    
    print("\n" + "=" * 50)
    print("✅ Database seeding completed successfully!")
    print("\n📝 Sample Accounts:")
    print("   Volunteers:")
    print("   - volunteer1@example.com / password123")
    print("   - volunteer2@example.com / password123")
    print("   - volunteer3@example.com / password123")
    print("\n   Organizations:")
    print("   - org1@example.com / password123")
    print("   - org2@example.com / password123")
    print("   - org3@example.com / password123")
    print("\n🌐 You can now test the UI with realistic data!")

if __name__ == '__main__':
    main()
