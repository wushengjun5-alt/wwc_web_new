from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_add_shipping_name_to_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='b2b_rejection_reason',
            field=models.TextField(blank=True, help_text='Internal note on why the B2B request was rejected', verbose_name='B2B Rejection Reason'),
        ),
        migrations.AddField(
            model_name='customer',
            name='b2b_approved_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='B2B Approved/Rejected At'),
        ),
    ]
