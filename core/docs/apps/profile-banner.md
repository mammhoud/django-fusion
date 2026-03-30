# Profile Banner Options

This document lists the available and recommended options for the profile banner actions dropdown in AllianceCore.

**Source component:** `components/profile/partials/banner-options.html`

---

## Current Implementation

### Signed-In User (Own Profile)
- **Share Profile** — Share the profile via social media or link
- **Settings** — Navigate to account settings

### Visitor (Other User's Profile)
- **Follow** — Follow/unfollow the user
- **Message** — Send a direct message
- **Share Profile** — Share the profile
- **Report** — Report the user for violations

---

## Additional Options to Consider

### For Signed-In User (Own Profile)

#### Primary Actions

- **Edit Profile** — Direct button to edit profile information
  - Icon: `bi-pencil` | Type: Primary button
  - Route: `{% url 'handlers:profile-edit' %}`

- **View as Public** — Preview how profile appears to others
  - Icon: `bi-eye` | Type: Dropdown item
  - Opens profile in new tab without auth context

#### Profile Management

- **Profile Visibility** — Toggle profile public/private
  - Icon: `bi-lock` / `bi-unlock` | Type: Dropdown item with toggle
  - AJAX action to update visibility field

- **Export Profile Data** — Download profile information
  - Icon: `bi-download` | Type: Dropdown item
  - Generates downloadable JSON/PDF

- **QR Code** — Generate QR code for profile
  - Icon: `bi-qr-code` | Type: Dropdown item
  - Opens modal with QR code

#### Account Actions

- **Activity Log** — View recent account activity
  - Icon: `bi-clock-history`
  - Route: `{% url 'handlers:activity-log' %}`

- **Privacy Settings** — Quick access to privacy controls
  - Icon: `bi-shield-check`
  - Route: `{% url 'handlers:privacy' %}`

- **Logout** — Sign out of account
  - Icon: `bi-box-arrow-right` | Styled: danger
  - Route: `{% url 'pipelines:logout' %}`

---

### For Visitors (Other User's Profile)

#### Interaction Actions

- **Block User** — Prevent user from viewing your profile
  - Icon: `bi-slash-circle` | Styled: danger
  - Opens confirmation modal

- **Mute Notifications** — Stop notifications from this user
  - Icon: `bi-bell-slash` | AJAX toggle

- **Add to List** — Add user to a custom list/group
  - Icon: `bi-collection`
  - Opens modal to select/create list

#### Information Actions

- **View Mutual Connections** — See shared followers/following
  - Icon: `bi-people`
  - Route: `{% url 'handlers:mutual-connections' user_id=user.id %}`

- **View Activity** — See public activity/posts
  - Icon: `bi-activity`
  - Route: `{% url 'handlers:user-activity' user_id=user.id %}`

- **Copy Profile Link** — Quick copy profile URL
  - Icon: `bi-link-45deg` | JavaScript clipboard action

#### Safety Actions

- **Report Profile** — Report inappropriate content *(already implemented)*
  - Icon: `bi-flag` | Styled: danger | Opens report modal

- **Block and Report** — Combined action for serious violations
  - Icon: `bi-exclamation-octagon` | Styled: danger | Opens combined modal

---

## Implementation Examples

### Edit Profile Button (Signed-In)

```django
<a href="{% url 'handlers:profile-edit' %}" class="profile__action btn btn-primary">
    <i class="bi bi-pencil me-1"></i>{% trans "Edit Profile" %}
</a>
```

### Block User Option (Visitor)

```django
<li>
    <a class="dropdown-item text-danger" href="#"
       data-bs-toggle="modal"
       data-bs-target="#confirmationModal"
       data-block-user-id="{{ user.id }}"
       data-block-user-name="{{ user.get_full_name|default:user.username }}">
        <i class="bi bi-slash-circle me-2"></i>{% trans "Block User" %}
    </a>
</li>
```

### Copy Profile Link

```django
<li>
    <a class="dropdown-item" href="#" id="copy-profile-link">
        <i class="bi bi-link-45deg me-2"></i>{% trans "Copy Profile Link" %}
    </a>
</li>

<script>
document.getElementById('copy-profile-link').addEventListener('click', function(e) {
    e.preventDefault();
    navigator.clipboard.writeText(window.location.href);
    // Show success toast/message
});
</script>
```

---

## Design Considerations

### Order of Priority
1. **Most Used First** — Place frequently used actions at the top
2. **Destructive Last** — Place dangerous actions (Block, Report) at the bottom
3. **Dividers** — Use `<hr class="dropdown-divider">` to group related actions

### Visual Hierarchy
- **Primary Actions** — Standalone buttons (Follow, Edit, etc.)
- **Secondary Actions** — First items in dropdown
- **Settings/Utils** — Middle of dropdown
- **Dangerous Actions** — Bottom with `text-danger` class

### Mobile Considerations
- Keep dropdowns to 5–7 items maximum for mobile usability
- Consider grouping similar actions into sub-menus if more options are needed
- Ensure touch targets are at least 44px height

### Internationalization
- Always wrap text in `{% trans %}` tags
- Keep action labels short (1–2 words)
- Icons should complement, not replace, text
