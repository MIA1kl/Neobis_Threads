# Generated by Django 4.2.4 on 2023-08-15 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('thread', '0004_rename_reposted_thread_thread_quoted_thread_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thread',
            name='quoted_content',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='quoted_image',
        ),
    ]