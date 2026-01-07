from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0009_remove_lead_latitude_remove_lead_longitude_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meeting',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='longitude',
        ),
        migrations.AddField(
            model_name='meeting',
            name='coordinates',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
