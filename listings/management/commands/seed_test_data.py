import random
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.models import User
from listings.models import Listing, ListingImage
from bookings.models import Booking
from payments.models import FeaturedSubscription, Payout
from refunds.models import RefundRequest

class Command(BaseCommand):
    help = 'Seed 25+ test listings with realistic data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding test data...')

        # ---------- USERS ----------
        customer, _ = User.objects.get_or_create(
            email='customer@demo.com',
            defaults={
                'username': 'customer@demo.com',
                'display_name': 'Demo Customer',
                'phone': '+251 911 111 111',
                'role': 'customer',
                'password': make_password('password123'),
                'is_active': True,
                'fayda_fin': '1234567890',
                'cbe_bank_account': 'CBE-1000-12345',
                'telebirr_phone': '+251 911 111 111',
                'cbe_birr_phone': '+251 911 111 111',
            }
        )

        landlord, _ = User.objects.get_or_create(
            email='landlord@demo.com',
            defaults={
                'username': 'landlord@demo.com',
                'display_name': 'Demo Landlord',
                'phone': '+251 922 222 222',
                'role': 'landlord',
                'password': make_password('password123'),
                'is_active': True,
                'fayda_fin': '9876543210',
                'cbe_bank_account': 'CBE-1000-54321',
                'telebirr_phone': '+251 922 222 222',
                'cbe_birr_phone': '+251 922 222 222',
            }
        )

        # ---------- LISTINGS (25+) ----------
        # Predefined images (Unsplash)
        image_pool = [
            'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1528605248644-14dd04022da1?auto=format&fit=crop&w=800&q=80',
        ]

        cities = ['Bole', 'CMC', 'Kazanchis', 'Old Airport', 'Mexico', 'Ayat', 'Summit', 'Lideta', 'Sarbet', 'Addis Ababa']
        categories = ['Apartment', 'House', 'Villa', 'Studio']

        listing_data = []

        for i in range(1, 26):
            city = random.choice(cities)
            category = random.choice(categories)
            bedrooms = random.randint(1, 5)
            bathrooms = random.randint(1, 3)
            kitchen = random.randint(1, 2)
            living_room = random.randint(1, 2)
            price = random.choice([5000, 7000, 10000, 15000, 20000, 25000, 30000, 40000, 50000])
            is_featured = random.choice([True, False])
            status = 'active' if random.random() > 0.2 else 'pending'

            title = f"{random.choice(['Luxury', 'Modern', 'Cozy', 'Spacious', 'Elegant'])} " \
                    f"{category} in {city} " \
                    f"{random.choice(['with Garden', 'with Pool', 'with Balcony', 'with Parking', 'with Security'])}"

            description = f"Beautiful {bedrooms}-bedroom {category} located in the heart of {city}. " \
                          f"Features: {bedrooms} beds, {bathrooms} baths, {kitchen} kitchen, {living_room} living room. " \
                          f"{random.choice(['Fully furnished', 'Semi-furnished', 'Unfurnished'])}. " \
                          f"{random.choice(['Close to schools, malls, and public transport.', 'Quiet neighborhood with 24/7 security.', 'Great view of the city skyline.'])}"

            listing_data.append({
                'title': title,
                'description': description,
                'price_per_month': price,
                'city': city,
                'address': f"{random.randint(1, 200)} {random.choice(['Main St', 'Bole Rd', 'CMC Rd', 'Kazanchis St', 'Old Airport Rd', 'Mexico St'])}",
                'google_maps_link': f'https://maps.google.com/?q={city}+Addis+Ababa',
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'kitchen': kitchen,
                'living_room': living_room,
                'category': category,
                'status': status,
                'is_featured': is_featured,
                'image_urls': random.sample(image_pool, random.randint(1, 3)),
            })

        for data in listing_data:
            image_urls = data.pop('image_urls', [])
            listing, created = Listing.objects.get_or_create(
                title=data['title'],
                landlord=landlord,
                defaults=data
            )
            if created:
                for url in image_urls:
                    ListingImage.objects.create(listing=listing, image=url)
                self.stdout.write(f'Created listing: {listing.title}')

        # ---------- BOOKING ----------
        active_listing = Listing.objects.filter(status='active').first()
        if active_listing:
            months = random.randint(2, 6)
            total_rent = active_listing.price_per_month * months
            # Convert to Decimal for multiplication
            commission_rate = Decimal('0.05')
            customer_commission = total_rent * commission_rate
            landlord_commission = total_rent * commission_rate
            total_paid = total_rent + customer_commission

            booking, _ = Booking.objects.get_or_create(
                customer=customer,
                listing=active_listing,
                defaults={
                    'months': months,
                    'total_rent': total_rent,
                    'customer_commission': customer_commission,
                    'landlord_commission': landlord_commission,
                    'total_paid': total_paid,
                    'status': 'paid',
                    'payment_reference': 'demo-pay-ref',
                    'paid_at': timezone.now(),
                    'google_maps_revealed': True,
                }
            )
            self.stdout.write(f'Created booking for {customer.display_name} on {active_listing.title}')

        # ---------- REFUND ----------
        if active_listing and booking:
            refund, _ = RefundRequest.objects.get_or_create(
                booking=booking,
                customer=customer,
                landlord=landlord,
                defaults={
                    'description': 'Misleading photos – AC missing and water leakage.',
                    'misleading_photos': ['https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=400&q=80'],
                    'reality_photos': ['https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=400&q=80'],
                    'status': 'pending',
                }
            )
            self.stdout.write(f'Created refund request for booking {booking.id}')

        # ---------- FEATURED SUBSCRIPTION (no 'plan' field) ----------
        featured_listing = Listing.objects.filter(is_featured=True).first()
        if featured_listing:
            # FeaturedSubscription model does not have 'plan' field; use 'quantity' and 'total_amount'
            sub, _ = FeaturedSubscription.objects.get_or_create(
                landlord=landlord,
                defaults={
                    'quantity': 1,
                    'total_amount': 500,
                    'end_date': timezone.now() + timedelta(days=30),
                    'status': 'active',
                    'payment_reference': 'demo-feat-ref',
                }
            )
            sub.listings.add(featured_listing)
            self.stdout.write(f'Created featured subscription for {featured_listing.title}')

        # ---------- PAYOUT ----------
        if active_listing and booking:
            payout, _ = Payout.objects.get_or_create(
                booking=booking,
                landlord=landlord,
                defaults={
                    'amount': booking.total_rent - booking.landlord_commission,
                    'status': 'pending',
                }
            )
            self.stdout.write(f'Created pending payout for landlord {landlord.display_name}')

        self.stdout.write(self.style.SUCCESS(f'✅ Seeded {len(listing_data)} listings, users, bookings, refunds, featured, and payouts.'))