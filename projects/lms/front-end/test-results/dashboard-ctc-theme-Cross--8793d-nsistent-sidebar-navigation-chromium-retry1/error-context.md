# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-ctc-theme.spec.ts >> Cross-page CTC Theme Consistency >> All dashboard pages share consistent sidebar navigation
- Location: tests/e2e/dashboard-ctc-theme.spec.ts:204:7

# Error details

```
Test timeout of 30000ms exceeded.
```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - banner [ref=e3]:
      - generic [ref=e5]:
        - link "CTC Research" [ref=e6] [cursor=pointer]:
          - /url: /
          - img [ref=e7]
          - generic [ref=e9]: CTC Research
        - navigation [ref=e10]:
          - link "Home" [ref=e11] [cursor=pointer]:
            - /url: /
          - link "About" [ref=e12] [cursor=pointer]:
            - /url: /about-us
          - link "Services" [ref=e13] [cursor=pointer]:
            - /url: /services
          - link "Team" [ref=e14] [cursor=pointer]:
            - /url: /team
          - link "Courses" [ref=e15] [cursor=pointer]:
            - /url: /courses
          - link "Blog" [ref=e16] [cursor=pointer]:
            - /url: /blog
          - link "Contact" [ref=e17] [cursor=pointer]:
            - /url: /contact
        - generic [ref=e19]:
          - link "Log In" [ref=e20] [cursor=pointer]:
            - /url: /login
          - link "Sign Up" [ref=e21] [cursor=pointer]:
            - /url: /registration
    - main [ref=e22]:
      - generic [ref=e24]:
        - complementary [ref=e25]:
          - navigation [ref=e26]:
            - link "Overview" [ref=e27] [cursor=pointer]:
              - /url: /dashboard
              - img [ref=e28]
              - text: Overview
            - link "My Courses" [ref=e30] [cursor=pointer]:
              - /url: /dashboard/enrolled-courses
              - img [ref=e31]
              - text: My Courses
            - link "Quizzes" [ref=e33] [cursor=pointer]:
              - /url: /dashboard/quiz
              - img [ref=e34]
              - text: Quizzes
            - link "My Assignments" [ref=e36] [cursor=pointer]:
              - /url: /dashboard/my-assignments
              - img [ref=e37]
              - text: My Assignments
            - link "Announcements" [ref=e40] [cursor=pointer]:
              - /url: /dashboard/announcement
              - img [ref=e41]
              - text: Announcements
            - link "My Attempts" [ref=e43] [cursor=pointer]:
              - /url: /dashboard/attempts
              - img [ref=e44]
              - text: My Attempts
            - link "History" [ref=e46] [cursor=pointer]:
              - /url: /dashboard/history
              - img [ref=e47]
              - text: History
            - link "Profile" [ref=e49] [cursor=pointer]:
              - /url: /dashboard/profile
              - img [ref=e50]
              - text: Profile
        - main [ref=e52]:
          - generic [ref=e54]:
            - img [ref=e56]
            - heading "Oops! An error occurred" [level=3] [ref=e58]
            - paragraph [ref=e59]: Please sign in to access your dashboard.
    - contentinfo [ref=e60]:
      - generic [ref=e61]:
        - generic [ref=e62]:
          - generic [ref=e63]:
            - link "CTC Research" [ref=e64] [cursor=pointer]:
              - /url: /
              - img [ref=e65]
              - generic [ref=e67]: CTC Research
            - paragraph [ref=e68]: Advancing clinical trials through innovation. Dedicated to accelerating the development of new therapies.
          - generic [ref=e69]:
            - heading "Research" [level=3] [ref=e70]
            - list [ref=e71]:
              - listitem [ref=e72]:
                - link "Our Services" [ref=e73] [cursor=pointer]:
                  - /url: /services
              - listitem [ref=e74]:
                - link "Our Team" [ref=e75] [cursor=pointer]:
                  - /url: /team
              - listitem [ref=e76]:
                - link "Training Courses" [ref=e77] [cursor=pointer]:
                  - /url: /courses
              - listitem [ref=e78]:
                - link "Research Blog" [ref=e79] [cursor=pointer]:
                  - /url: /blog
          - generic [ref=e80]:
            - heading "Support" [level=3] [ref=e81]
            - list [ref=e82]:
              - listitem [ref=e83]:
                - link "Contact Us" [ref=e84] [cursor=pointer]:
                  - /url: /contact
              - listitem [ref=e85]:
                - link "About CTC" [ref=e86] [cursor=pointer]:
                  - /url: /about-us
              - listitem [ref=e87]:
                - link "FAQ" [ref=e88] [cursor=pointer]:
                  - /url: /faq
              - listitem [ref=e89]:
                - link "Privacy Policy" [ref=e90] [cursor=pointer]:
                  - /url: /privacy
          - generic [ref=e91]:
            - heading "Get Involved" [level=3] [ref=e92]
            - list [ref=e93]:
              - listitem [ref=e94]:
                - link "Join a Trial" [ref=e95] [cursor=pointer]:
                  - /url: /registration
              - listitem [ref=e96]:
                - link "Partner With Us" [ref=e97] [cursor=pointer]:
                  - /url: /contact
        - paragraph [ref=e99]: © 2026 CTC Research. All rights reserved.
  - button "Select language" [ref=e102] [cursor=pointer]:
    - img [ref=e103]
    - generic [ref=e105]: EN
  - alert [ref=e106]
```