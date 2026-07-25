# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard-ctc-theme.spec.ts >> Cross-page CTC Theme Consistency >> CTC primary CSS variables are defined
- Location: tests/e2e/dashboard-ctc-theme.spec.ts:189:7

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
    - main [ref=e22]
    - contentinfo [ref=e30]:
      - generic [ref=e31]:
        - generic [ref=e32]:
          - generic [ref=e33]:
            - link "CTC Research" [ref=e34] [cursor=pointer]:
              - /url: /
              - img [ref=e35]
              - generic [ref=e37]: CTC Research
            - paragraph [ref=e38]: Advancing clinical trials through innovation. Dedicated to accelerating the development of new therapies.
          - generic [ref=e39]:
            - heading "Research" [level=3] [ref=e40]
            - list [ref=e41]:
              - listitem [ref=e42]:
                - link "Our Services" [ref=e43] [cursor=pointer]:
                  - /url: /services
              - listitem [ref=e44]:
                - link "Our Team" [ref=e45] [cursor=pointer]:
                  - /url: /team
              - listitem [ref=e46]:
                - link "Training Courses" [ref=e47] [cursor=pointer]:
                  - /url: /courses
              - listitem [ref=e48]:
                - link "Research Blog" [ref=e49] [cursor=pointer]:
                  - /url: /blog
          - generic [ref=e50]:
            - heading "Support" [level=3] [ref=e51]
            - list [ref=e52]:
              - listitem [ref=e53]:
                - link "Contact Us" [ref=e54] [cursor=pointer]:
                  - /url: /contact
              - listitem [ref=e55]:
                - link "About CTC" [ref=e56] [cursor=pointer]:
                  - /url: /about-us
              - listitem [ref=e57]:
                - link "FAQ" [ref=e58] [cursor=pointer]:
                  - /url: /faq
              - listitem [ref=e59]:
                - link "Privacy Policy" [ref=e60] [cursor=pointer]:
                  - /url: /privacy
          - generic [ref=e61]:
            - heading "Get Involved" [level=3] [ref=e62]
            - list [ref=e63]:
              - listitem [ref=e64]:
                - link "Join a Trial" [ref=e65] [cursor=pointer]:
                  - /url: /registration
              - listitem [ref=e66]:
                - link "Partner With Us" [ref=e67] [cursor=pointer]:
                  - /url: /contact
        - paragraph [ref=e69]: © 2026 CTC Research. All rights reserved.
  - button "Select language" [ref=e72] [cursor=pointer]:
    - img [ref=e73]
    - generic [ref=e75]: EN
```