# Generated by Django 4.1.5 on 2023-02-03 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0003_upvotequestion_upvoteanswer_downvotequestion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downvotequestion',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downvote_question', to='post.question'),
        ),
    ]
