# Generated by Django 5.0.4 on 2024-05-18 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals_auth', '0006_alter_customuser_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.CharField(default='ba0b7a25fd244792a26b366d48892b28', max_length=64, primary_key=True, serialize=False),
        ),
    ]
