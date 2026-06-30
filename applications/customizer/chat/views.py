from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.defaultfilters import linebreaksbr
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .models import Conversation, Message
from .forms import ConversationStartForm, MessageForm
from .services import ConversationService
from .customizer import customizer_apps
from .constants import (
    RECENT_CONVERSATIONS_LIMIT,
    ERROR_MESSAGES,
    AI_DISPLAY_NAME,
    AI_AVATAR_TEXT,
    get_model,
    default_model_id,
    model_choices,
)


def render_markdown(content):
    """Convert markdown to HTML safely"""
    return linebreaksbr(escape(content))


@method_decorator(csrf_exempt, name="dispatch")
class HomepageView(ListView):
    """TemplateTinker homepage showing recent conversations."""
    
    model = Conversation
    template_name = "homepage.html"
    context_object_name = "recent_conversations"
    queryset = Conversation.objects.all().order_by("-updated_at")[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customizer_apps"] = customizer_apps()
        context["model_choices"] = model_choices()
        context["default_model_id"] = default_model_id()
        context["default_model_name"] = (
            get_model(default_model_id()) or {}
        ).get("name", "Gemma 3 4B")
        return context

    def post(self, request, *args, **kwargs):
        """Handle new conversation creation from homepage."""
        message_content = request.POST.get("message", "").strip()
        model_id = request.POST.get("model_id", "gemma3-4b")

        if not message_content:
            return HttpResponse("Message cannot be empty", status=400)

        # Create new conversation
        conversation = Conversation.objects.create(
            title=(
                message_content[:50] + "..."
                if len(message_content) > 50
                else message_content
            )
        )

        # Save the initial message
        Message.objects.create(
            conversation=conversation, content=message_content, is_user=True
        )

        # Redirect to the new chat where streaming will occur
        return redirect(f"{reverse('chat', kwargs={'conversation_id': conversation.id})}?model_id={model_id}")



@method_decorator(csrf_exempt, name="dispatch")
class ChatView(DetailView):
    """Individual chat conversation view - handles both GET and POST"""
    
    model = Conversation
    template_name = "chat.html"
    context_object_name = "conversation"
    pk_url_kwarg = "conversation_id"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation = self.object
        model_id = self.request.GET.get("model_id", "gemma3-4b")
        
        # Process messages for display
        messages_with_content = []
        for message in conversation.messages.all():
            if message.is_user:
                # User messages: simple line breaks
                formatted_content = linebreaksbr(escape(message.content))
            else:
                # AI messages: render markdown
                formatted_content = render_markdown(message.content)
            
            messages_with_content.append(
                {"original": message, "formatted_content": formatted_content}
            )
        
        context.update({
            "messages": conversation.messages.all(),
            "messages_with_content": messages_with_content,
            "customizer_apps": customizer_apps(),
            "model_id": model_id,
        })
        return context

    def post(self, request, conversation_id):
        """Handle new messages in existing chat - returns HTML with SSE endpoint info"""
        message_content = request.POST.get("message", "").strip()
        model_id = request.POST.get("model_id") or request.GET.get("model_id", "gemma3-4b")
        model_name = (get_model(model_id) or {}).get("name", "AI")

        if not message_content:
            return HttpResponse(ERROR_MESSAGES["EMPTY_MESSAGE"], status=400)

        conversation = get_object_or_404(Conversation, id=conversation_id)

        # Save user message using service
        user_message = ConversationService.add_user_message(
            conversation, message_content
        )

        # Format user content
        user_formatted = linebreaksbr(escape(user_message.content))

        # Return user message HTML and placeholder for AI response with SSE
        return HttpResponse(
            f"""
            <!-- User Message -->
            <div class="d-flex justify-content-end mb-3 fade-in">
                <div class="message-bubble user-message rounded-3 px-3 py-2">
                    <div class="mb-1">{user_formatted}</div>
                    <small class="opacity-75">{user_message.timestamp.astimezone().strftime('%I:%M %p').lstrip('0').replace(' 0', ' ')}</small>
                </div>
            </div>

            <!-- AI Message Placeholder -->
            <div class="d-flex justify-content-start mb-3 fade-in" id="ai-response-{user_message.id}">
                <div class="me-2">
                    <div class="ai-avatar rounded-circle d-flex align-items-center justify-content-center fw-bold">
                        G3
                    </div>
                </div>
                <div class="message-bubble ai-message rounded-3 px-3 py-2">
                    <div class="mb-1 text-break markdown-content" id="ai-content-{user_message.id}"></div>
                    <small class="text-muted" id="ai-timestamp-{user_message.id}"></small>
                </div>
            </div>

            <!-- SSE Script for Streaming -->
            <script>
                const eventSource = new EventSource('/chat/{conversation.id}/stream/?message_id={user_message.id}&model_id={model_id}');
                let aiContent = '';
                const contentDiv = document.getElementById('ai-content-{user_message.id}');
                const timestampDiv = document.getElementById('ai-timestamp-{user_message.id}');
                
                eventSource.onmessage = function(event) {{
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'token') {{
                        aiContent += data.content;
                        contentDiv.textContent = aiContent;
                    }} else if (data.type === 'done') {{
                        timestampDiv.innerHTML = data.timestamp + ' • {model_name}';
                        eventSource.close();
                        // Convert markdown to HTML
                        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
                        if (csrfToken) {{
                            fetch('/chat/{conversation.id}/render-markdown/', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': csrfToken.value
                                }},
                                body: JSON.stringify({{content: aiContent}})
                            }})
                            .then(response => response.text())
                            .then(html => {{
                                contentDiv.innerHTML = html;
                                hljs.highlightAll();
                            }});
                        }} else {{
                            // Fallback if no CSRF token - just display raw content
                            contentDiv.innerHTML = aiContent;
                        }}
                    }}
                }};
                
                eventSource.onerror = function(event) {{
                    console.error('SSE error:', event);
                    console.error('ReadyState:', eventSource.readyState);
                    eventSource.close();
                    contentDiv.innerHTML = '<em>Error: Connection lost. Check console for details.</em>';
                }};
            </script>
        """
        )


class WebsiteListView(ListView):
    """List websites available to the customizer."""

    template_name = "websites.html"
    context_object_name = "websites"

    def get_queryset(self):
        from .site_data import configured_websites

        return configured_websites()


class PagesEndpointView(DetailView):
    """Return page cards with sections linked to each page."""

    template_name = "pages.html"

    def get(self, request, *args, **kwargs):
        from django.http import JsonResponse

        from .site_data import pages_for_website

        data = pages_for_website(kwargs["website_slug"])
        if data is None:
            return JsonResponse({"error": "Unknown website"}, status=404)
        wants_json = (
            request.headers.get("Accept") == "application/json"
            or request.GET.get("format") == "json"
        )
        if wants_json:
            return JsonResponse(data)
        return self.render_to_response(data)


class PageNavigatorFragmentView(ListView):
    """HTMX fragment containing website navigation links."""

    template_name = "fragments/page_navigator.html"
    context_object_name = "websites"

    def get_queryset(self):
        from .site_data import configured_websites

        return configured_websites()


class PageCardGridFragmentView(DetailView):
    """HTMX fragment containing page cards for a selected website."""

    template_name = "fragments/page_card_grid.html"

    def get(self, request, *args, **kwargs):
        from django.http import Http404

        from .site_data import pages_for_website

        data = pages_for_website(kwargs["website_slug"])
        if data is None:
            raise Http404("Unknown website")
        return self.render_to_response(data)


class PageSectionListFragmentView(DetailView):
    """HTMX fragment containing sections linked to one page card."""

    template_name = "fragments/page_section_list.html"

    def get(self, request, *args, **kwargs):
        from django.http import Http404

        from .site_data import pages_for_website

        data = pages_for_website(kwargs["website_slug"])
        if data is None:
            raise Http404("Unknown website")
        page_path = kwargs["page_path"]
        page = next(
            (item for item in data["pages"] if item["path"] == page_path),
            None,
        )
        if page is None:
            raise Http404("Unknown page")
        return self.render_to_response({"website": data["website"], "page": page})


class MessageSendResultFragmentView(FormMixin, ListView):
    """HTMX fragment showing the result of a message-send action."""

    form_class = MessageForm
    template_name = "fragments/message_send_result.html"

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        context = {
            "form": form,
            "message": (
                request.POST.get("content")
                or request.POST.get("message", "")
            ),
            "is_success": form.is_valid(),
        }
        return self.render_to_response(context, status=200 if form.is_valid() else 400)
