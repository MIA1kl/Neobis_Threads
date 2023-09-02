# Generated by Django 4.2.4 on 2023-08-26 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thread', '0005_remove_thread_quoted_content_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(max_length=200),
        ),
        migrations.AlterField(
            model_name='thread',
            name='content',
            field=models.TextField(blank=True, default='', max_length=200),
        ),
    ]
