# Generated by Django 3.2.6 on 2021-08-28 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_rename_categoty_product_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='sell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]