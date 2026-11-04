from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('home','0005_importedimage')]
    operations = [migrations.AlterField(model_name='brandsettings', name='company_ar', field=models.CharField(default='KFATA',max_length=150))]
