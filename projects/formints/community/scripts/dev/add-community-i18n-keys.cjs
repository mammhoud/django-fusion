#!/usr/bin/env node
/* Idempotent: adds Community refund + offline-mode keys to every locale if missing. */
const fs = require('fs');
const path = require('path');

const I18N_DIR = path.join(__dirname, '..', '..', 'src', 'i18n');
const LOCALES = ['en.json', 'fr.json', 'de.json', 'es.json', 'ar.json'];

const KEYS = {
  common: {
    offlineMode: {
      en: 'Offline mode — data stays on this device',
      fr: 'Mode hors ligne — les données restent sur cet appareil',
      de: 'Offline-Modus — Daten bleiben auf diesem Gerät',
      es: 'Modo sin conexión — los datos permanecen en este dispositivo',
      ar: 'وضع عدم الاتصال — تبقى البيانات على هذا الجهاز',
    },
  },
  transactions: {
    refund: { en: 'Refund', fr: 'Rembourser', de: 'Erstatten', es: 'Reembolsar', ar: 'استرداد' },
    refundTitle: { en: 'Refund sale', fr: 'Rembourser la vente', de: 'Verkauf erstatten', es: 'Reembolsar venta', ar: 'استرداد عملية البيع' },
    refundMessage: {
      en: 'Refund sale #{id} for {amount}?',
      fr: 'Rembourser la vente #{id} pour {amount} ?',
      de: 'Verkauf #{id} für {amount} erstatten?',
      es: '¿Reembolsar la venta #{id} por {amount}?',
      ar: 'استرداد عملية البيع رقم #{id} بمبلغ {amount}؟',
    },
    confirmRefund: { en: 'Confirm refund', fr: 'Confirmer le remboursement', de: 'Erstattung bestätigen', es: 'Confirmar reembolso', ar: 'تأكيد الاسترداد' },
    refunding: { en: 'Refunding…', fr: 'Remboursement…', de: 'Erstatte…', es: 'Reembolsando…', ar: 'جارٍ الاسترداد…' },
    refundSuccess: { en: 'Refund successful', fr: 'Remboursement réussi', de: 'Erstattung erfolgreich', es: 'Reembolso exitoso', ar: 'تم الاسترداد بنجاح' },
    refundError: { en: 'Refund failed', fr: 'Échec du remboursement', de: 'Erstattung fehlgeschlagen', es: 'Error en el reembolso', ar: 'فشل الاسترداد' },
    refunded: { en: 'Refunded', fr: 'Remboursé', de: 'Erstattet', es: 'Reembolsado', ar: 'مسترجع' },
  },
};

let changed = false;
for (const file of LOCALES) {
  const fp = path.join(I18N_DIR, file);
  const locale = file.replace('.json', '');
  const json = JSON.parse(fs.readFileSync(fp, 'utf8'));
  for (const [section, keys] of Object.entries(KEYS)) {
    if (!json[section]) json[section] = {};
    for (const [key, translations] of Object.entries(keys)) {
      if (!(key in json[section])) {
        json[section][key] = translations[locale];
        changed = true;
        console.log(`added ${file} ${section}.${key}`);
      }
    }
  }
  fs.writeFileSync(fp, JSON.stringify(json, null, 2) + '\n');
}
if (!changed) console.log('no new keys — all locales up to date');
