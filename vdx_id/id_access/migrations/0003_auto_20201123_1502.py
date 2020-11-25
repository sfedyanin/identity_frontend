# Generated by Django 2.2.10 on 2020-11-23 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('id_work_agent', '0001_initial'),
        ('id_accounts', '0001_initial'),
        ('id_platforms', '0001_initial'),
        ('id_identities', '0001_initial'),
        ('id_access', '0002_viaccessitemrequest_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='viaccessitemrequest',
            name='account_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='access_item_requests', to='id_work_agent.ViAccountTemplate'),
        ),
        migrations.AddField(
            model_name='viaccessitemrequest',
            name='identity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_item_requests', to='id_identities.VdxIdentity'),
        ),
        migrations.AddField(
            model_name='viaccessitemrequest',
            name='platform',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='access_item_requests', to='id_platforms.ViPlatform'),
        ),
        migrations.AddField(
            model_name='viaccessitem',
            name='members',
            field=models.ManyToManyField(through='id_access.AccessItemMembership', to='id_accounts.ViAccount'),
        ),
        migrations.AddField(
            model_name='viaccessitem',
            name='platform',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='access_items', to='id_platforms.ViPlatform'),
        ),
        migrations.AddField(
            model_name='viaccessgrouprequest',
            name='access_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='access_group_requests', to='id_access.ViAccessGroup'),
        ),
        migrations.AddField(
            model_name='viaccessgrouprequest',
            name='attention_identities',
            field=models.ManyToManyField(blank=True, related_name='auth_attention', to='id_identities.VdxIdentity'),
        ),
        migrations.AddField(
            model_name='viaccessgrouprequest',
            name='identity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='access_group_requests', to='id_identities.VdxIdentity'),
        ),
        migrations.AddField(
            model_name='viaccessgrouprequest',
            name='parent_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_group_requests', to='id_access.ViAccessGroupRequest'),
        ),
        migrations.AddField(
            model_name='viaccessgroupchangerequest',
            name='access_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_requests', to='id_access.ViAccessGroup'),
        ),
        migrations.AddField(
            model_name='viaccessgroup',
            name='access_groups',
            field=models.ManyToManyField(blank=True, related_name='inheriting_groups', to='id_access.ViAccessGroup'),
        ),
        migrations.AddField(
            model_name='viaccessgroup',
            name='access_items',
            field=models.ManyToManyField(blank=True, related_name='inheriting_groups', to='id_access.ViAccessItem'),
        ),
        migrations.AddField(
            model_name='viaccessgroup',
            name='members',
            field=models.ManyToManyField(through='id_access.AccessGroupMembership', to='id_identities.VdxIdentity'),
        ),
        migrations.AddField(
            model_name='viaccessgroup',
            name='owners',
            field=models.ManyToManyField(related_name='owned_access_groups', to='id_identities.VdxIdentity'),
        ),
        migrations.AddField(
            model_name='viaccessgroup',
            name='platform',
            field=models.ForeignKey(blank=True, help_text='The Platform associated to AccessItems if present', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='associated_groups', to='id_platforms.ViPlatform'),
        ),
        migrations.AddField(
            model_name='accessitemmembership',
            name='access',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accessitem_memberships', to='id_access.ViAccessItem'),
        ),
        migrations.AddField(
            model_name='accessitemmembership',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accessitem_memberships', to='id_accounts.ViAccount'),
        ),
        migrations.AddField(
            model_name='accessgroupmembership',
            name='access_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accessgroup_memberships', to='id_access.ViAccessGroup'),
        ),
        migrations.AddField(
            model_name='accessgroupmembership',
            name='identity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accessgroup_memberships', to='id_identities.VdxIdentity'),
        ),
        migrations.AlterUniqueTogether(
            name='viaccessitemrequest',
            unique_together={('identity', 'platform', 'access_item')},
        ),
        migrations.AlterUniqueTogether(
            name='viaccessitem',
            unique_together={('identifier', 'platform')},
        ),
    ]