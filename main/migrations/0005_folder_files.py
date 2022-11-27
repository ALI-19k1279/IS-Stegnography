# Generated by Django 4.1.3 on 2022-11-27 08:02

from django.db import migrations, models
import django.db.models.deletion
import main.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_stegno_filename_alter_stegno_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=main.models.get_upload_path)),
                ('created_at', models.DateField(auto_now=True)),
                ('folder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.folder')),
            ],
        ),
    ]