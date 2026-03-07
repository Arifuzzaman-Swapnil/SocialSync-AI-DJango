from django.db import migrations, models
import ai_image.models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_image', '0005_add_prompt_engineering_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagegeneration',
            name='copy_overlay_image',
            field=models.ImageField(blank=True, help_text='Image with copy text overlay applied', null=True, upload_to=ai_image.models.generated_image_path),
        ),
        migrations.AddField(
            model_name='imagegeneration',
            name='copy_overlay_text',
            field=models.CharField(blank=True, default='', help_text='The copy text overlaid on the image', max_length=200),
        ),
        migrations.AddField(
            model_name='imagegeneration',
            name='copy_overlay_settings',
            field=models.JSONField(blank=True, help_text='Overlay styling settings (position, font, color, etc.)', null=True),
        ),
    ]
