# Generated by Django 4.2.16 on 2024-10-09 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_remove_ippool_router'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ippool',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
