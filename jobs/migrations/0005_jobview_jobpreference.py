# Generated migration for behavioral tracking

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jobs', '0004_jobapplication_rejection_reason'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('time_spent_seconds', models.PositiveIntegerField(default=0, help_text='Time spent viewing this job in seconds')),
                ('source', models.CharField(choices=[('search', 'Search'), ('recommendations', 'Recommendations'), ('browse', 'Browse'), ('direct', 'Direct')], default='browse', max_length=20)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='jobs.job')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_views', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-viewed_at'],
                'indexes': [
                    models.Index(fields=['user', '-viewed_at'], name='jobs_jobvie_user_id_viewed_idx'),
                    models.Index(fields=['job', '-viewed_at'], name='jobs_jobvie_job_id_viewed_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='JobPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preference_type', models.CharField(choices=[('applied', 'Applied'), ('rejected', 'Rejected'), ('saved', 'Saved'), ('ignored', 'Ignored')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to='jobs.job')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_preferences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('user', 'job', 'preference_type')},
            },
        ),
    ]
