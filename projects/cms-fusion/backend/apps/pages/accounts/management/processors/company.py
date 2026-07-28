import logging

from django.core.exceptions import FieldError
from django.db.models import Q

from apps.core.domain.contrib.models import Contact, ContactEmail, ContactPhone
from apps.core.domain.contrib.models import Corporate as Company

# from commons.contact.models.profile import Company

logger = logging.getLogger(__name__)


def contacts_list(fields=None, context=None, filters=None, search=None):
    """
    Retrieves all contacts, optionally limiting to specified fields, applying filters, and performing a search.

    :param fields: Optional list of fields to return for each contact.
    :param context: Optional context to extend.
    :param filters: Optional dictionary of filters to apply (e.g., {'name__icontains': 'John'}).
    :param search: Optional search term to apply across multiple fields.
    :return: Queryset of contacts with optional field selection, filtering, and searching.
    """
    contacts = Contact.objects.all()

    # Apply filters if provided
    if filters:
        try:
            contacts = contacts.filter(**filters)
        except (TypeError, ValueError, FieldError) as e:
            logger.warning("Error applying filters: %s", e)
            return None

    # Apply search if provided
    if search:
        try:
            contacts = contacts.filter(
                Q(name__icontains=search)  # Assuming the Contact model has a 'name' field
                | Q(emails__email__icontains=search)  # Search in related emails
                | Q(phones__phone_number__icontains=search)  # Search in related phone numbers
            ).distinct()
        except (TypeError, ValueError, FieldError) as e:
            logger.warning("Error applying search: %s", e)
            return None

    # Select specific fields if provided
    if fields:
        try:
            contacts = contacts.values(*fields)
        except (TypeError, FieldError) as e:
            logger.warning("Error selecting fields: %s", e)
            return None

    # Update the context if provided
    if context is not None:
        context.update({"contacts": contacts})
        return context

    return contacts


def contact_details(contact, fields=None):
    """
    Retrieves detailed information for a single contact, including emails and phones.

    :param contact: A Contact object or ID.
    :param fields: Optional list of additional fields to include.
    :return: A context dictionary with contact details or None if not found.
    """
    if isinstance(contact, int):
        try:
            contact = Contact.objects.get(pk=contact)
        except Contact.DoesNotExist:
            logger.warning("Contact with id %s does not exist.", contact)
            return None

    emails = ContactEmail.objects.filter(contact=contact).values_list("email", flat=True)
    phones = ContactPhone.objects.filter(contact=contact).values_list("phone_number", flat=True)

    context = {
        "contact": contact,
        "emails": list(emails),
        "phones": list(phones),
    }

    # Optionally add extra fields
    if fields:
        context.update({field: getattr(contact, field, None) for field in fields})

    return context


def contact_company(contact):
    """
    Returns the company associated with a given contact.

    :param contact: A Contact object or ID.
    :return: A Company queryset or None if not found.
    """
    if isinstance(contact, int):
        try:
            contact = Contact.objects.get(pk=contact)
        except Contact.DoesNotExist:
            logger.warning("Contact with id %s does not exist.", contact)
            return None

    company = Company.objects.filter(pk=contact.added_company).first()

    return company


def company_contacts(company):
    """
    Retrieves all contacts associated with a given company.

    :param company: A Company object or ID.
    :return: A queryset of contacts associated with the company.
    """
    if isinstance(company, int):
        try:
            company = Company.objects.get(pk=company)
        except Company.DoesNotExist:
            logger.warning("Company with id %s does not exist.", company)
            return None

    contacts = Contact.objects.filter(added_company=company)

    return contacts


def company_contacts_details(company):
    """
    Retrieves detailed information for all contacts associated with a given company.

    :param company: A Company object or ID.
    :return: A list of context dictionaries with contact details.
    """
    if isinstance(company, int):
        try:
            company = Company.objects.get(pk=company)
        except Company.DoesNotExist:
            logger.warning("Company with id %s does not exist.", company)
            return None

    contacts = company_contacts(company)

    # Use the `contact_details` function to prepare detailed information for each contact
    context = [contact_details(contact) for contact in contacts]

    return context
