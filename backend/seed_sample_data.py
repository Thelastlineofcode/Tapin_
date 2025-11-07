"""
Seed the database with fun sample listings
Run with: python seed_sample_data.py
"""
import sys
from app import app, db, Listing, User
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Listing.query.delete()
        
        # Create sample users (organizations)
        print("Creating sample users/organizations...")
        
        users = [
            User(
                email="deathrow@records.com",
                password_hash=generate_password_hash("sample123")
            ),
            User(
                email="nwa@compton.com",
                password_hash=generate_password_hash("sample123")
            ),
            User(
                email="badboy@entertainment.com",
                password_hash=generate_password_hash("sample123")
            ),
        ]
        
        for user in users:
            existing = User.query.filter_by(email=user.email).first()
            if not existing:
                db.session.add(user)
        
        db.session.commit()
        
        # Get the user IDs
        deathrow_user = User.query.filter_by(email="deathrow@records.com").first()
        nwa_user = User.query.filter_by(email="nwa@compton.com").first()
        badboy_user = User.query.filter_by(email="badboy@entertainment.com").first()
        
        # Create sample listings
        print("Creating sample listings...")
        
        listings = [
            Listing(
                title="Death Row Records - Janitorial Services",
                description="Keep the studio clean while Tupac records his next hit! We need someone who can handle late nights, occasional spills, and keeping the vibe immaculate. Previous experience with gold records preferred but not required.",
                location="Los Angeles, CA",
                owner_id=deathrow_user.id if deathrow_user else 1
            ),
            Listing(
                title="N.W.A Community Garden Project",
                description="Straight Outta Compton... into organic farming! Help us turn vacant lots into thriving gardens. Volunteers will learn urban agriculture while giving back to the community. Snoop Dogg might drop by with gardening tips.",
                location="Compton, CA",
                owner_id=nwa_user.id if nwa_user else 1
            ),
            Listing(
                title="Bad Boy Entertainment - Event Setup Crew",
                description="Diddy needs help setting up for the next big party! Looking for energetic volunteers to help with stage setup, lighting, and making sure everything is on point. Must be able to lift 50+ lbs and have impeccable taste in music.",
                location="New York, NY",
                owner_id=badboy_user.id if badboy_user else 1
            ),
            Listing(
                title="Tupac's Poetry Workshop Assistant",
                description="2Pac is hosting poetry workshops for youth and needs teaching assistants. Help inspire the next generation of spoken word artists. Must love poetry, hip-hop culture, and have patience with aspiring poets.",
                location="Oakland, CA",
                owner_id=deathrow_user.id if deathrow_user else 1
            ),
            Listing(
                title="Ice Cube's Film Production Internship",
                description="Friday just got real! Help with independent film production, from script reading to on-set assistance. Learn the business from a legend. Must be available weekends and ready to work hard.",
                location="Los Angeles, CA",
                owner_id=nwa_user.id if nwa_user else 1
            ),
            Listing(
                title="Biggie's Food Truck Volunteer",
                description="Notorious B.I.G. Memorial Food Truck serving the community. Need volunteers to help serve meals, take orders, and spread love through good food. All meals served with extra Brooklyn attitude (in a good way).",
                location="Brooklyn, NY",
                owner_id=badboy_user.id if badboy_user else 1
            ),
            Listing(
                title="Dr. Dre's Beat Making Workshop Helper",
                description="Forgot About Dre? Never! Help organize music production workshops for underprivileged youth. Assist with equipment setup, student registration, and keeping the energy high. No production experience needed.",
                location="Los Angeles, CA",
                owner_id=nwa_user.id if nwa_user else 1
            ),
            Listing(
                title="Tupac Shakur Youth Center - Sports Coordinator",
                description="Makaveli lives on through youth basketball! Organize pickup games, coach fundamentals, and be a positive role model. If you've got game and heart, we want you on the team.",
                location="Oakland, CA",
                owner_id=deathrow_user.id if deathrow_user else 1
            ),
        ]
        
        for listing in listings:
            db.session.add(listing)
        
        db.session.commit()
        
        print(f"\n✅ Successfully created {len(listings)} sample listings!")
        print("\nSample organizations:")
        print("- Death Row Records (deathrow@records.com)")
        print("- N.W.A (nwa@compton.com)")
        print("- Bad Boy Entertainment (badboy@entertainment.com)")
        print("\nPassword for all: sample123")
        print("\nVolunteers mentioned: Tupac, Snoop Dogg, Diddy, Ice Cube, Biggie, Dr. Dre")

if __name__ == "__main__":
    try:
        seed_data()
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        sys.exit(1)
