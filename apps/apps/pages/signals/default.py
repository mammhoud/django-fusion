import logging

from django.contrib.auth.models import Group  # ✅ Use Django's built-in Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    Create default Django Groups after migrations.
    
    Groups created:
        - Instructors
        - Students
        - Supervisors
        - Admins (optional)
        - Moderators (optional)
    """

    # Optional: Limit to specific app(s) if needed
    # if sender.name not in ["apps.pages", "auth"]:
    #     return

    DEFAULT_GROUPS = [
        {
            "name": "Instructors",
            "description": "Users with instructor privileges. Can create and manage courses."
        },
        {
            "name": "Students",
            "description": "Regular users enrolled in courses."
        },
        {
            "name": "Supervisors",
            "description": "Users who can oversee multiple instructors and courses."
        },
        {
            "name": "Admins",
            "description": "System administrators with full access.",
            "optional": True  # Only create if not exists
        },
        {
            "name": "Moderators",
            "description": "Users who can moderate content and users.",
            "optional": True
        },
    ]

    created_count = 0
    existing_count = 0

    for group_data in DEFAULT_GROUPS:
        group_name = group_data["name"]
        description = group_data.get("description", "")
        is_optional = group_data.get("optional", False)

        # Try to get or create the group
        try:
            group, created = Group.objects.get_or_create(
                name=group_name,
                defaults={"name": group_name}  # Django Group only has 'name' field
            )

            if created:
                created_count += 1
                logger.info(f"✅ Created default group: '{group_name}'")

                # Add description if needed (requires custom Group model)
                # group.description = description
                # group.save()

            else:
                existing_count += 1
                if not is_optional:
                    logger.debug(f"📋 Group already exists: '{group_name}'")

        except Exception as e:
            logger.error(f"❌ Failed to create group '{group_name}': {e!s}")
            continue

    # Log summary
    if created_count > 0:
        logger.info(f"🎯 Created {created_count} default groups, {existing_count} already existed.")

    return created_count


# Optional: Add permissions to groups after creation
@receiver(post_migrate)
def assign_default_permissions(sender, **kwargs):
    """
    Assign default permissions to groups.
    Run this AFTER create_default_groups.
    """
    if sender.name != "contenttypes":
        return

    from django.contrib.auth.models import Permission

    # Define permission assignments
    GROUP_PERMISSIONS = {
        "Admins": ["add_user", "change_user", "delete_user", "view_user"],
        "Instructors": ["add_course", "change_course", "view_course"],
        "Moderators": ["change_user", "view_user", "delete_comment"],
    }

    for group_name, perm_codenames in GROUP_PERMISSIONS.items():
        try:
            group = Group.objects.get(name=group_name)

            for codename in perm_codenames:
                try:
                    # Permission format: <app_label>.<codename>
                    if '.' in codename:
                        app_label, perm_codename = codename.split('.')
                    else:
                        # Try to find permission (less precise)
                        perm = Permission.objects.filter(codename=codename).first()
                        if perm:
                            group.permissions.add(perm)
                except Exception as e:
                    logger.debug(f"Could not add permission '{codename}' to '{group_name}': {e}")

        except Group.DoesNotExist:
            continue  # Group doesn't exist (might be optional)
