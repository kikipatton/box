# Generated by Django 4.2.16 on 2024-10-13 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0005_alter_pppoeservice_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='pppoeservice',
            name='mikrotik_secret_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
