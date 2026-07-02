# listings/management/commands/seed_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import random
from accounts.models import User
from listings.models import Listing, ListingImage
from bookings.models import Booking
from payments.models import FeaturedSubscription, Payout

class Command(BaseCommand):
    help = 'Seed test data for demo'

    def handle(self, *args, **options):
        self.stdout.write('Seeding test data...')

        # 1. Create users
        customer, _ = User.objects.get_or_create(
            email='customer@demo.com',
            defaults={
                'username': 'customer@demo.com',
                'display_name': 'Demo Customer',
                'phone': '+251 911 111 111',
                'role': 'customer',
                'password': make_password('password123'),
                'is_active': True,
                'is_profile_complete': True,
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
                'is_profile_complete': True,
                'fayda_fin': '9876543210',
                'cbe_bank_account': 'CBE-1000-54321',
                'telebirr_phone': '+251 922 222 222',
                'cbe_birr_phone': '+251 922 222 222',
            }
        )

        # 2. Create listings (5 active, 1 pending, 1 booked)
        listings_data = [
            {
                'title': 'Luxury Villa in Old Airport',
                'description': 'Stunning 4-bedroom villa with garden and pool.',
                'price_per_month': 25000,
                'city': 'Old Airport',
                'address': 'Near International Community School',
                'google_maps_link': 'https://maps.google.com/?q=Old+Airport+Addis+Ababa',
                'bedrooms': 4,
                'bathrooms': 3,
                'kitchen': 1,
                'living_room': 1,
                'category': 'Villa',
                'status': 'active',
                'is_featured': True,
                'image_urls': [
                    'https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80',
                    'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80',
                ]
            },
            {
                'title': 'Modern Apartment in Bole',
                'description': 'Fully furnished 2-bedroom apartment near Edna Mall.',
                'price_per_month': 18000,
                'city': 'Bole',
                'address': 'Behind Edna Mall',
                'google_maps_link': 'https://maps.google.com/?q=Bole+Edna+Mall+Addis+Ababa',
                'bedrooms': 2,
                'bathrooms': 2,
                'kitchen': 1,
                'living_room': 1,
                'category': 'Apartment',
                'status': 'active',
                'is_featured': False,
                'image_urls': [
                    'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80',
                ]
            },
            {
                'title': 'Cozy Studio in CMC',
                'description': 'Compact studio with modern amenities.',
                'price_per_month': 8000,
                'city': 'CMC',
                'address': 'Near Ayat Roundabout',
                'google_maps_link': 'https://maps.google.com/?q=CMC+Addis+Ababa',
                'bedrooms': 1,
                'bathrooms': 1,
                'kitchen': 1,
                'living_room': 1,
                'category': 'Studio',
                'status': 'active',
                'is_featured': False,
                'image_urls': [
                    'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80',
                ]
            },
            {
                'title': 'Family House in Kazanchis',
                'description': 'Spacious 3-bedroom house with parking.',
                'price_per_month': 22000,
                'city': 'Kazanchis',
                'address': 'Near UNECA',
                'google_maps_link': 'https://maps.google.com/?q=Kazanchis+Addis+Ababa',
                'bedrooms': 3,
                'bathrooms': 2,
                'kitchen': 1,
                'living_room': 1,
                'category': 'House',
                'status': 'active',
                'is_featured': True,
                'image_urls': [
                    'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80',
                ]
            },
            {
                'title': 'Penthouse in Mexico Area',
                'description': 'Luxury penthouse with panoramic views.',
                'price_per_month': 35000,
                'city': 'Mexico',
                'address': 'Opposite Wabi Shebelle Hotel',
                'google_maps_link': 'https://maps.google.com/?q=Mexico+Addis+Ababa',
                'bedrooms': 3,
                'bathrooms': 3,
                'kitchen': 1,
                'living_room': 1,
                'category': 'Apartment',
                'status': 'pending',   # pending approval
                'is_featured': False,
                'image_urls': [
                    'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80',
                ]
            },
        ]

        for data in listings_data:
            image_urls = data.pop('image_urls', [])
            listing, created = Listing.objects.get_or_create(
                title=data['title'],
                landlord=landlord,
                defaults=data
            )
            if created:
                # Add images (as image_url since we're using URLField)
                for url in image_urls:
                    ListingImage.objects.create(listing=listing, image_url=url)
                self.stdout.write(f'Created listing: {listing.title}')
            else:
                self.stdout.write(f'Listing already exists: {listing.title}')

        # 3. Create a booking (customer rents one active listing)
        active_listing = Listing.objects.filter(status='active', landlord=landlord).first()
        if active_listing:
            booking, _ = Booking.objects.get_or_create(
                customer=customer,
                listing=active_listing,
                defaults={
                    'months': 3,
                    'total_rent': active_listing.price_per_month * 3,
                    'customer_commission': active_listing.price_per_month * 3 * 0.05,
                    'landlord_commission': active_listing.price_per_month * 3 * 0.05,
                    'total_paid': active_listing.price_per_month * 3 * 1.05,
                    'status': 'paid',
                    'payment_reference': 'demo-pay-ref',
                    'paid_at': timezone.now(),
                    'google_maps_revealed': True,
                }
            )
            self.stdout.write(f'Created booking for {customer.display_name} on {active_listing.title}')

        # 4. Create a pending refund request for that booking
        if active_listing:
            refund, _ = RefundRequest.objects.get_or_create(
                booking=booking,
                customer=customer,
                landlord=landlord,
                defaults={
                    'description': 'Misleading photos – AC missing.',
                    'misleading_photos': ['https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=400&q=80'],
                    'reality_photos': ['https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=400&q=80'],
                    'status': 'pending',
                }
            )
            self.stdout.write(f'Created refund request for booking {booking.id}')

        # 5. Create a FeaturedSubscription for a listing
        featured_listing = Listing.objects.filter(is_featured=True).first()
        if featured_listing:
            sub, _ = FeaturedSubscription.objects.get_or_create(
                landlord=landlord,
                listing=featured_listing,
                defaults={
                    'plan': 'monthly',
                    'quantity': 1,
                    'total_amount': 500,
                    'end_date': timezone.now() + timedelta(days=30),
                    'status': 'active',
                    'payment_reference': 'demo-feat-ref',
                }
            )
            self.stdout.write(f'Created featured subscription for {featured_listing.title}')

        # 6. Create a pending Payout for the landlord
        if active_listing:
            payout, _ = Payout.objects.get_or_create(
                booking=booking,
                landlord=landlord,
                defaults={
                    'amount': booking.total_rent - booking.landlord_commission,
                    'status': 'pending',
                }
            )
            self.stdout.write(f'Created pending payout for landlord {landlord.display_name}')

        self.stdout.write(self.style.SUCCESS('Test data seeding complete!'))