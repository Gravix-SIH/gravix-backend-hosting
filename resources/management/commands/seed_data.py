from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from bookings.models import Booking
from resources.models import Resource, ResourceBookmark
from users.models import User


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Create counselors if not exist
        counselors_data = [
            {
                'username': 'counselor1',
                'email': 'counselor1@avenu.com',
                'name': 'Dr. Priya Sharma',
                'department': 'Stress & Anxiety Management',
                'role': 'counsellor',
            },
            {
                'username': 'counselor2',
                'email': 'counselor2@avenu.com',
                'name': 'Dr. Rahul Verma',
                'department': 'Sleep & Lifestyle Therapy',
                'role': 'counsellor',
            },
            {
                'username': 'counselor3',
                'email': 'counselor3@avenu.com',
                'name': 'Dr. Ananya Gupta',
                'department': 'Cognitive Behavioral Therapy',
                'role': 'counsellor',
            },
        ]

        counselors = []
        for data in counselors_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults=data
            )
            if created:
                user.set_password('counselor123')
                user.save()
            counselors.append(user)
            self.stdout.write(f'  Counselor: {user.name}')

        # Create sample resources
        resources_data = [
            {
                'title': 'Meditation Techniques for Students',
                'description': 'Learn essential meditation practices to manage academic stress and improve focus.',
                'type': 'article',
                'url': 'https://example.com/meditation-guide',
                'category': 'Mindfulness',
                'duration': '15 min',
                'rating': 4.8,
            },
            {
                'title': 'Healthy Sleep Habits Guide',
                'description': 'Improve your sleep quality with these evidence-based sleep hygiene tips.',
                'type': 'article',
                'url': 'https://example.com/sleep-guide',
                'category': 'Sleep Health',
                'duration': '10 min',
                'rating': 4.9,
            },
            {
                'title': 'Time Management Strategies',
                'description': 'Master your time with proven productivity techniques for academic success.',
                'type': 'video',
                'url': 'https://example.com/time-management',
                'category': 'Productivity',
                'duration': '20 min',
                'rating': 4.7,
            },
            {
                'title': 'Breathing Exercises for Anxiety',
                'description': 'Simple yet powerful breathing techniques to reduce anxiety on demand.',
                'type': 'audio',
                'url': 'https://example.com/breathing',
                'category': 'Stress Relief',
                'duration': '8 min',
                'rating': 4.6,
            },
            {
                'title': 'Understanding Your Mental Health',
                'description': 'A comprehensive guide to mental health awareness for college students.',
                'type': 'document',
                'url': 'https://example.com/mental-health',
                'category': 'Education',
                'duration': '30 min',
                'rating': 4.9,
            },
            {
                'title': 'Mindful Eating Practices',
                'description': 'Develop a healthier relationship with food through mindful eating techniques.',
                'type': 'article',
                'url': 'https://example.com/mindful-eating',
                'category': 'Nutrition',
                'duration': '12 min',
                'rating': 4.5,
            },
        ]

        for data in resources_data:
            resource, created = Resource.objects.get_or_create(
                title=data['title'],
                defaults={**data, 'created_by': counselors[0]}
            )
            if created:
                self.stdout.write(f'  Resource: {resource.title}')

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
