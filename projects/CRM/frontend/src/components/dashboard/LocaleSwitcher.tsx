import { useEffect, useState } from 'react';

interface LanguageOption {
  code: string;
  label: string;
  direction: 'ltr' | 'rtl';
}

interface LocalePayload {
  current: string;
  direction: 'ltr' | 'rtl';
  languages: LanguageOption[];
}

function csrfToken(): string {
  return document.cookie.match(/(?:^|; )csrftoken=([^;]*)/)?.[1] ?? '';
}

function applyDocumentLocale(next: LocalePayload): void {
  document.documentElement.lang = next.current;
  document.documentElement.dir = next.direction;
}

export default function LocaleSwitcher() {
  const [payload, setPayload] = useState<LocalePayload | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void fetch('/apis/core/locale/', { credentials: 'include' })
      .then((response) => (response.ok ? response.json() as Promise<LocalePayload> : null))
      .then((next) => { if (next) { setPayload(next); applyDocumentLocale(next); } })
      .catch(() => undefined);
  }, []);

  async function changeLocale(language: string) {
    if (!payload || language === payload.current || busy) return;
    setBusy(true);
    try {
      const response = await fetch('/apis/core/locale/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
        body: JSON.stringify({ language }),
      });
      if (!response.ok) return;
      const next = await response.json() as LocalePayload;
      setPayload(next);
      applyDocumentLocale(next);
      window.location.reload();
    } finally {
      setBusy(false);
    }
  }

  if (!payload || payload.languages.length < 2) return null;

  return (
    <label className="loop-locale-switcher">
      <span>Language</span>
      <select
        aria-label="Interface language"
        value={payload.current}
        disabled={busy}
        onChange={(event) => void changeLocale(event.target.value)}
      >
        {payload.languages.map((language) => (
          <option value={language.code} key={language.code}>{language.label}</option>
        ))}
      </select>
    </label>
  );
}
