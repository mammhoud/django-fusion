from django.db import models

from .mapping import RelationType
from .relationsManager import RelationsManager


# Define your models
class MyModel(models.Model):
    name = models.CharField(max_length=255)


# Initialize the RelationsManager
relations_manager = RelationsManager()

# Example: Get table data
filters = {"name__icontains": "example"}
order_by = ["name"]
table_data = relations_manager.Generics().get_table_data(
    model=MyModel, filters=filters, order_by=order_by, page=1, page_size=10
)
print(table_data)

# Example: Bulk assign relation
related_instance = MyModel.objects.get(id=1)
objects_to_assign = MyModel.objects.filter(name__icontains="example")
relations_manager.Generics().bulk_assign_relation(
    service_name=RelationType.CATEGORY,
    objects=list(objects_to_assign),
    related_instance=related_instance,
)

# Example: Get relation stats
relation_stats = relations_manager.Generics().get_relation_stats(
    service_name=RelationType.CATEGORY, model=MyModel
)
print(relation_stats)

# Example: Export table data to CSV
csv_data = relations_manager.Generics().export_table_data(
    model=MyModel, format="csv", filters=filters, order_by=order_by
)
print(csv_data)
