from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from wagtail.models import GroupPagePermission, Page, Collection, GroupCollectionPermission, Workflow, WorkflowTask, WorkflowPage, GroupApprovalTask


class Command(BaseCommand):
    help = 'Create dedicated KFATA editorial roles. Existing unrelated groups are untouched.'

    def handle(self, **options):
        root = Page.get_first_root_node()
        collection = Collection.get_first_root_node()
        for name, publish in [('KFATA Editors',False),('KFATA Publishers',True),('KFATA Managers',True)]:
            group, _ = Group.objects.get_or_create(name=name)
            page_actions = ['add','change','lock'] + (['publish','bulk_delete','delete'] if publish else [])
            for action in page_actions:
                permission = Permission.objects.get(content_type__app_label='wagtailcore',codename=f'{action}_page')
                GroupPagePermission.objects.get_or_create(group=group,page=root,permission=permission)
            group.permissions.add(Permission.objects.get(content_type__app_label='wagtailadmin',codename='access_admin'))
            for app, model in [('wagtailimages','image'),('wagtaildocs','document')]:
                for action in ['add','change']:
                    perm = Permission.objects.get(content_type__app_label=app,codename=f'{action}_{model}')
                    GroupCollectionPermission.objects.get_or_create(group=group,collection=collection,permission=perm)
            if name == 'KFATA Managers':
                group.permissions.add(*Permission.objects.filter(content_type__app_label='home',content_type__model__in=['brandsettings','enquiry']))
        workflow,_ = Workflow.objects.get_or_create(name='KFATA publishing',defaults={'active':True})
        task,_ = GroupApprovalTask.objects.get_or_create(name='KFATA publisher approval',defaults={'active':True})
        task.groups.add(*Group.objects.filter(name__in=['KFATA Publishers','KFATA Managers']))
        WorkflowTask.objects.get_or_create(workflow=workflow,task=task,defaults={'sort_order':0})
        assignment = WorkflowPage.objects.filter(page=root).first()
        if not assignment:
            WorkflowPage.objects.create(page=root,workflow=workflow)
        elif assignment.workflow.name == 'Moderators approval':
            assignment.workflow=workflow;assignment.save(update_fields=['workflow'])
        self.stdout.write(self.style.SUCCESS('KFATA roles configured. Assign accounts deliberately; superusers manage users and groups.'))
