# Generated by Django 5.0.5 on 2024-05-20 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals_auth', '0009_alter_customuser_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.CharField(default='c2f35ad15d47415d99f54127cb3e61a6', max_length=64, primary_key=True, serialize=False),
        ),
    ]
