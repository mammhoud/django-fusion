"""Management command to load course fixtures."""

import logging

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django_fusion.site.management.commands.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Load course fixtures (courses, tags, specializations)."""

    help = 'Load course fixtures (courses, tags, specializations)'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed loading information',
        )

    def handle(self, *args, **options):
        """Execute the command."""
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('📚 LOADING COURSE FIXTURES'))
        self.stdout.write(self.style.SUCCESS('=' * 60 + '\n'))
        
        # Ensure we have an instructor user
        self._ensure_instructor_user()
        
        try:
            # Load specializations
            self.stdout.write('Loading specializations...')
            call_command('loaddata', 'assets/fixtures/lms/specializations.json', verbosity=2 if verbose else 0)
            self.stdout.write(self.style.SUCCESS('✓ Specializations loaded\n'))
            
            # Load course tags
            self.stdout.write('Loading course tags...')
            call_command('loaddata', 'assets/fixtures/lms/course_tags.json', verbosity=2 if verbose else 0)
            self.stdout.write(self.style.SUCCESS('✓ Course tags loaded\n'))
            
            # Load courses
            self.stdout.write('Loading courses...')
            call_command('loaddata', 'assets/fixtures/lms/courses.json', verbosity=2 if verbose else 0)
            self.stdout.write(self.style.SUCCESS('✓ Courses loaded\n'))
            
            # Show summary
            self._show_summary()
            
            self.stdout.write(self.style.SUCCESS('\n✅ All fixtures loaded successfully!\n'))
            self.stdout.write('🌐 Visit http://localhost:8000/courses/ to see courses\n')
            self.stdout.write('📊 Admin: http://localhost:8000/admin/\n')
            self.stdout.write(self.style.SUCCESS('=' * 60 + '\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error loading fixtures: {e}\n'))
            self.stdout.write(self.style.ERROR(f'Details: {str(e)}\n'))
            raise

    def _ensure_instructor_user(self):
        """Ensure instructor user exists."""
        instructor = User.objects.filter(username='instructor').first()
        if not instructor:
            instructor = User.objects.create_user(
                'instructor',
                'instructor@example.com',
                'secure_password_123'
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created instructor user (ID: {instructor.id})\n'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Using existing instructor user (ID: {instructor.id})\n'))

    def _show_summary(self):
        """Show a summary of loaded data."""
        from apps.pages.lms.models import Course, CourseTag, Specialization
        
        courses_count = Course.objects.count()
        tags_count = CourseTag.objects.count()
        specialization_count = Specialization.objects.count()
        published_courses = Course.objects.filter(is_published=True, is_active=True).count()
        featured_courses = Course.objects.filter(is_featured=True).count()
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('📊 FIXTURE SUMMARY')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Total Courses:         {courses_count}')
        self.stdout.write(f'Published Courses:     {published_courses}')
        self.stdout.write(f'Featured Courses:      {featured_courses}')
        self.stdout.write(f'Course Tags:           {tags_count}')
        self.stdout.write(f'Specializations:       {specialization_count}')
        self.stdout.write('=' * 60 + '\n')
