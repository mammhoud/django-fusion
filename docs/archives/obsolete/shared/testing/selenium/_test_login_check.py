import requests

def test_site(base_url, label):
    s = requests.Session()
    r = s.get(f"{base_url}/auth/sign-in/?next=/admin/")
    csrf = s.cookies.get('csrftoken', '')
    print(f"{label} CSRF: {csrf[:20]}")
    r2 = s.post(
        f"{base_url}/auth/sign-in/",
        data={
            'login': 'admin',
            'password': 'mk_pAssWord123',
            'csrfmiddlewaretoken': csrf,
            'next': '/admin/'
        },
        headers={'Referer': f"{base_url}/auth/sign-in/"},
        allow_redirects=True
    )
    print(f"{label} Login: {r2.status_code} {r2.url[:80]}")
    print(f"{label} Has admin: {'/admin/' in r2.url}")
    # Try wagtail admin
    r3 = s.get(f"{base_url}/admin/", allow_redirects=True)
    print(f"{label} Admin direct: {r3.status_code} {r3.url[:80]}")

test_site("http://localhost:8280", "CORE")
test_site("http://localhost:8271", "WEBSITE")
