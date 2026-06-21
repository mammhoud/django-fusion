from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from crafts_ai.content.models.newsletter import Campaign, Subscriber


class SubscriberViewSet(SnippetViewSet):
    model = Subscriber
    icon = "user"
    menu_label = "Subscribers"
    list_display = ["email", "name", "status", "created_at"]
    list_filter = ["status", "source"]
    search_fields = ["email", "name"]

class CampaignViewSet(SnippetViewSet):
    model = Campaign
    icon = "mail"
    menu_label = "Campaigns"
    list_display = ["name", "subject", "status", "total_sent", "sent_at"]
    list_filter = ["status"]
    search_fields = ["name", "subject"]

class NewsletterSnippetGroup(SnippetViewSetGroup):
    menu_label = "Newsletter"
    menu_icon = "mail"
    menu_order = 500
    items = (SubscriberViewSet, CampaignViewSet)
