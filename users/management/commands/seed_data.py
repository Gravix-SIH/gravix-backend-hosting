import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User
from bookings.models import Booking
from resources.models import Resource, ResourceBookmark
from assessments.models import Assessment
from chat.models import ChatSession, ChatMessage


class Command(BaseCommand):
    help = "Seed the database with sample data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear all existing seed data before seeding",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=20,
            help="Number of student users to create (default: 20)",
        )

    def handle(self, *args, **options):
        clear = options["clear"]
        num_students = options["users"]

        if clear:
            self.clear_data()

        self.stdout.write("Seeding database...\n")

        # Create admin
        admin = self.create_admin()

        # Create counsellor
        counsellors = self.create_counsellors()

        # Create students
        students = self.create_students(num_students)

        # Create resources
        resources = self.create_resources(admin)

        # Create bookings
        self.create_bookings(students, counsellors)

        # Create assessments
        self.create_assessments(students)

        # Create chat sessions
        self.create_chat_sessions(students)

        # Create bookmarks
        self.create_bookmarks(students, resources)

        self.stdout.write(self.style.SUCCESS("\nDatabase seeded successfully!"))
        self.stdout.write(
            f"  Admin: admin@gravix.com / password123\n"
            f"  Counsellors: {len(counsellors)}\n"
            f"  Students: {len(students)}\n"
            f"  Resources: {len(resources)}\n"
            f"  Bookings, assessments, chat sessions created"
        )

    def clear_data(self):
        self.stdout.write("Clearing existing data...")
        ChatMessage.objects.all().delete()
        ChatSession.objects.all().delete()
        ResourceBookmark.objects.all().delete()
        Assessment.objects.all().delete()
        Booking.objects.all().delete()
        Resource.objects.all().delete()
        # Keep admin/counsellor/student users that were seeded
        User.objects.filter(email__startswith="seed_").delete()
        self.stdout.write("  Cleared.\n")

    def create_admin(self):
        user, created = User.objects.get_or_create(
            email="admin@gravix.com",
            defaults={
                "username": "admin@gravix.com",
                "name": "System Admin",
                "role": "admin",
                "is_active": True,
                "is_verified": True,
            },
        )
        if created:
            user.set_password("password123")
            user.save()
            self.stdout.write(f"  Created admin: {user.email}")
        else:
            self.stdout.write(f"  Admin exists: {user.email}")
        return user

    def create_counsellors(self):
        data = [
            ("Dr. Priya Sharma", "priya@gravix.com", "Clinical Psychology"),
            ("Dr. Raj Patel", "raj@gravix.com", "Psychiatry"),
            ("Dr. Ananya Singh", "ananya@gravix.com", "Counseling Psychology"),
            ("Dr. Vikram Kumar", "vikram@gravix.com", "Clinical Psychology"),
        ]
        counsellors = []
        for name, email, dept in data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "name": name,
                    "role": "counsellor",
                    "department": dept,
                    "is_active": True,
                    "is_verified": True,
                },
            )
            if created:
                user.set_password("password123")
                user.save()
                self.stdout.write(f"  Created counsellor: {email}")
            counsellors.append(user)
        return counsellors

    def create_students(self, count):
        first_names = [
            "Ravi", "Anita", "Karan", "Meera", "Sanjay", "Priya", "Amit", "Neha",
            "Vikram", "Kavita", "Arjun", "Sunita", "Deepak", "Ritu", "Mohit", "Pooja",
            "Rajesh", "Anita", "Suresh", "Gita", "Harish", "Lakshmi", "Naresh", "Sita",
            "Ravi", "Anjali", "Vijay", "Richa", "Sanjay", "Priyanka",
        ]
        last_names = [
            "Kumar", "Singh", "Patel", "Sharma", "Reddy", "Joshi", "Mehta", "Gupta",
            "Verma", "Agarwal", "Chopra", "Malhotra", "Kapoor", "Sinha", "Nair",
            "Menon", "Iyer", "Rao", "Das", "Mukherjee", "Banerjee", "Chatterjee",
            "Shah", "Desai", "Parekh", "Modi", "Trivedi", "Pandey", "Mishra",
        ]
        students = []
        created = 0
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            email = f"seed_{first.lower()}_{last.lower()}_{i}@test.com"
            user, is_new = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "name": f"{first} {last}",
                    "role": "student",
                    "is_active": True,
                    "is_verified": True,
                },
            )
            if is_new:
                user.set_password("password123")
                user.save()
                created += 1
            students.append(user)

        self.stdout.write(f"  Created {created} student users ({count} total)")
        return students

    def create_resources(self, admin):
        data = [
            ("Understanding Anxiety", "article", "Learn about anxiety and coping strategies", "Mental Health", "10 min read"),
            ("Guided Meditation for Stress Relief", "audio", "A 15-minute guided meditation", "Relaxation", "15 min"),
            ("Sleep Hygiene Tips", "video", "Improve your sleep quality", "Sleep Health", "8 min"),
            ("Managing Exam Stress", "article", "Tips for students during exams", "Student Wellness", "5 min read"),
            ("Breathing Exercises for Calm", "article", "Simple breathing techniques", "Relaxation", "3 min read"),
            ("Depression: What You Need to Know", "article", "Understanding depression symptoms and help", "Mental Health", "12 min read"),
            ("Mindfulness Meditation Guide", "video", "Introduction to mindfulness", "Mindfulness", "20 min"),
            ("Healthy Sleep Habits", "document", "PDF guide to better sleep", "Sleep Health", "PDF"),
            ("Coping with Homesickness", "article", "Advice for new students", "Student Wellness", "7 min read"),
            ("Stress Management Workshop", "video", "Full workshop recording", "Mental Health", "45 min"),
            ("Self-Care for Students", "article", "Daily self-care practices", "Student Wellness", "6 min read"),
            ("Understanding Burnout", "article", "Recognize and address burnout", "Mental Health", "10 min read"),
            ("Relaxation Music Playlist", "audio", "Curated calming tracks", "Relaxation", "60 min"),
            ("Study-Life Balance Tips", "article", "Balancing academics and life", "Student Wellness", "8 min read"),
            ("Emergency Mental Health Resources", "link", "Crisis hotlines and contacts", "Mental Health", "Link"),
        ]
        resources = []
        for title, rtype, desc, cat, duration in data:
            res, created = Resource.objects.get_or_create(
                title=title,
                defaults={
                    "type": rtype,
                    "description": desc,
                    "url": f"https://example.com/{title.lower().replace(' ', '-')}",
                    "category": cat,
                    "duration": duration,
                    "rating": round(random.uniform(3.5, 5.0), 2),
                    "created_by": admin,
                },
            )
            resources.append(res)
        self.stdout.write(f"  Created {len(resources)} resources")
        return resources

    def create_bookings(self, students, counsellors):
        statuses = ["pending", "confirmed", "completed", "cancelled"]
        session_types = ["video", "in-person", "phone"]
        times = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]

        count = 0
        for student in random.sample(students, min(len(students), 15)):
            num_bookings = random.randint(1, 3)
            for _ in range(num_bookings):
                days_offset = random.randint(-30, 30)
                booking_date = timezone.now().date() + timedelta(days=days_offset)
                status = random.choice(statuses)
                counsellor = random.choice(counsellors)

                booking, created = Booking.objects.get_or_create(
                    student=student,
                    counsellor=counsellor,
                    date=booking_date,
                    time=random.choice(times),
                    defaults={
                        "session_type": random.choice(session_types),
                        "status": status,
                        "notes": f"Session booked for {student.name}",
                    },
                )
                if created:
                    count += 1

        self.stdout.write(f"  Created {count} bookings")

    def create_assessments(self, students):
        types = ["phq9", "gad7", "psqi"]
        count = 0
        for student in random.sample(students, min(len(students), 15)):
            for atype in random.sample(types, random.randint(1, 3)):
                if atype == "phq9":
                    score = random.randint(0, 27)
                    max_score = 27
                    severity = self.phq9_severity(score)
                elif atype == "gad7":
                    score = random.randint(0, 21)
                    max_score = 21
                    severity = self.gad7_severity(score)
                else:
                    score = random.randint(0, 21)
                    max_score = 21
                    severity = self.psqi_severity(score)

                answers = [random.randint(0, 3) for _ in range(9 if atype == "phq9" else 7 if atype == "gad7" else 19)]

                Assessment.objects.create(
                    user=student,
                    assessment_type=atype,
                    score=score,
                    max_score=max_score,
                    severity=severity,
                    answers=answers,
                )
                count += 1

        self.stdout.write(f"  Created {count} assessment submissions")

    def create_chat_sessions(self, students):
        count = 0
        messages_pool = [
            "I've been feeling really anxious lately about my exams",
            "Can you suggest some relaxation techniques?",
            "I'm having trouble sleeping at night",
            "What should I do when I feel overwhelmed?",
            "I've been feeling down for the past few weeks",
            "How can I manage stress better?",
            "I'm not able to concentrate on my studies",
            "Can we talk about mindfulness?",
        ]
        bot_responses = [
            "I understand. Let's talk about that.",
            "That sounds challenging. Have you tried deep breathing?",
            "It's okay to feel this way. Let's work through it together.",
            "Thank you for sharing. Here's a technique that might help...",
            "I'm here to support you. Let's explore some options.",
        ]

        for student in random.sample(students, min(len(students), 10)):
            session = ChatSession.objects.create(user=student)
            for i in range(random.randint(2, 5)):
                ChatMessage.objects.create(
                    session=session,
                    sender="user",
                    message=random.choice(messages_pool),
                )
                ChatMessage.objects.create(
                    session=session,
                    sender="bot",
                    message=random.choice(bot_responses),
                )
            count += 1

        self.stdout.write(f"  Created {count} chat sessions")

    def create_bookmarks(self, students, resources):
        count = 0
        for student in random.sample(students, min(len(students), 8)):
            for resource in random.sample(resources, random.randint(1, 4)):
                bookmark, created = ResourceBookmark.objects.get_or_create(
                    user=student,
                    resource=resource,
                )
                if created:
                    count += 1
        self.stdout.write(f"  Created {count} bookmarks")

    @staticmethod
    def phq9_severity(score):
        if score <= 4:
            return "Minimal"
        elif score <= 9:
            return "Mild"
        elif score <= 14:
            return "Moderate"
        elif score <= 19:
            return "Moderately Severe"
        return "Severe"

    @staticmethod
    def gad7_severity(score):
        if score <= 4:
            return "Minimal"
        elif score <= 9:
            return "Mild"
        elif score <= 14:
            return "Moderate"
        return "Severe"

    @staticmethod
    def psqi_severity(score):
        if score <= 5:
            return "Good"
        elif score <= 10:
            return "Fair"
        elif score <= 15:
            return "Poor"
        return "Very Poor"
