# Generated by Django 5.0.3 on 2024-05-08 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_alter_order_returned'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='returned',
        ),
        migrations.AddField(
            model_name='order',
            name='return_status',
            field=models.CharField(choices=[('Not Requested', 'Not Requested'), ('Requested', 'Requested'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Not Requested', max_length=50),
        ),
    ]