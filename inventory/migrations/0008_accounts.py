# Generated by Django 3.2.3 on 2021-08-28 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_sell_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='accounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tolal', models.IntegerField(default=0)),
                ('clearence', models.IntegerField(default=0)),
            ],
        ),
    ]
