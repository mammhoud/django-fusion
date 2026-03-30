from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from core.app.payloads import base  # type: ignore

from ..models import Contact
from ..preloads.contacts import contacts_list


class contactView(Panel):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        contacts = contacts_list()
        contacts = base(request, contacts)  # Get paginated contacts
        context.update({"contacts": contacts})
        # print(context["contacts"])
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for adding a contact using the form shown by the modal.
        """

        # if request.is_ajax():
        # Process AJAX request for adding a new contact
        name = request.POST.get("name")
        # is_primary = request.POST.get('is_primary')
        company = request.POST.get("company")
        job_title = request.POST.get("job_title")
        bio = request.POST.get("bio")
        phone_numbers = request.POST.getlist("phone_numbers")  # Assuming a list of phone numbers
        email_addresses = request.POST.getlist(
            "email_addresses"
        )  # Assuming a list of email addresses

        # Create a new Contact instance
        contact = Contact(
            name=name,
            is_primary=False,
            company=company,
            job_title=job_title,
            # createdby_id=self.request.user,
            bio=bio,
        )
        contact.save()

        # Associate phone numbers and email addresses
        for phone_number in phone_numbers:
            contact.phones.add(phone_number)  # type: ignore
        for email_address in email_addresses:
            contact.emails.add(email_address)  # type: ignore

        # Return a success response (e.g., JSON or HTML) indicating successful addition
        return JsonResponse({"success": True, "message": "Contact added successfully"})

        # else:
        #     # Handle non-AJAX requests (e.g., redirect or render a template)
        #     return HttpResponseRedirect(reverse('contact_list'))  # Assuming a 'contact_list' view


def CardsView(request, id):
    print(id)
    contact = get_object_or_404(Contact, id=id)

    # Prepare contact data for the card
    contact_data = {
        "title": f"{contact.name}",
        "description": contact.job_title,
        "bio": contact.bio,
        "phone": contact.phones.first().number  # type: ignore
        if contact.phones.exists()
        else None,
        # 'company': contact.company.name if contact.company else None,
        # 'date_added': contact.date_added.strftime('%Y-%m-%d'),
        # 'email': contact.emails.first().email if contact.emails.exists() else None,
        # 'image': contact.profile_image.url if contact.profile_image else None,  # Optional image
    }

    return JsonResponse(contact_data)


def search_contacts(request):
    query = request.GET.get("q", "")
    if query:
        # Search contacts by name, email, or phone number
        contacts = Contact.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
            # Q(email__icontains=query)
        )

        # Prepare the results in a dictionary format for JSON response
        results = {"contacts": list(contacts.values("first_name"))}

        return JsonResponse(results, safe=False)
    else:
        return JsonResponse({"error": "No query provided"}, status=400)


# Create your views here.
# contacts
apps_contacts_list_view = contactView.as_view(template_name="apps/contacts/list.html")
apps_contacts_profile_view = contactView.as_view(template_name="apps/contacts/profile.html")

# crm
apps_crm_customers_view = contactView.as_view(template_name="apps/crm/customers.html")
apps_crm_contacts_view = contactView.as_view(template_name="pages/contacts.html")
apps_crm_dashboard_view = contactView.as_view(template_name="apps/crm/dashboard.html")
apps_crm_leads_view = contactView.as_view(template_name="apps/crm/leads.html")
apps_crm_opportunities_view = contactView.as_view(template_name="apps/crm/opportunities.html")
