# Generated by Django 2.1 on 2018-08-18 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mile1', '0003_auto_20180818_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='review_count',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
