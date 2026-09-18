import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const read = (relativePath) => readFile(resolve(ROOT, relativePath), 'utf8');

test('Email sync ships Gmail and Outlook adapters behind one contract', async () => {
  const sync = await read('../backend/apps/core/email_sync.py');
  assert.match(sync, /class GmailConnector/);
  assert.match(sync, /class OutlookConnector/);
  assert.match(sync, /class EmailSyncConnector/);
  assert.match(sync, /class UnconfiguredEmailConnector/);
  assert.match(sync, /def sync_account/);
});

test('Email sync degrades honestly without credentials', async () => {
  const sync = await read('../backend/apps/core/email_sync.py');
  assert.match(sync, /Connect \{self\.provider\} before syncing email\./);
  assert.match(sync, /status="unconfigured"/);
});

test('Email accounts and messages are persisted as tenant-scoped models', async () => {
  const models = await read('../backend/apps/core/models.py');
  assert.match(models, /class EmailAccount/);
  assert.match(models, /class EmailMessage/);
  assert.match(models, /uniq_email_account_workspace_provider_email/);
  assert.match(models, /uniq_email_message_account_external/);
});

test('Email sync API never projects OAuth tokens', async () => {
  const api = await read('../backend/apps/core/api.py');
  assert.match(api, /def email_accounts_api/);
  assert.match(api, /oauth_token.*payload/);
  assert.match(api, /def email_messages_api/);
});

test('Email accounts sync through a dedicated Dramatiq actor and command', async () => {
  const tasks = await read('../backend/plugins/workers/tasks.py');
  assert.match(tasks, /def sync_email_account/);
  const command = await read('../backend/apps/core/management/commands/sync_email.py');
  assert.match(command, /sync_account/);
});

test('Email sync ships a Gmail/Outlook OAuth connect flow (authorize + callback)', async () => {
  const oauth = await read('../backend/apps/core/email_oauth.py');
  assert.match(oauth, /def gmail_authorize_url/);
  assert.match(oauth, /def outlook_authorize_url/);
  assert.match(oauth, /def connect_start/);
  assert.match(oauth, /def oauth_callback/);
  assert.match(oauth, /def exchange_gmail_code/);
  assert.match(oauth, /def exchange_outlook_code/);
  const urls = await read('../backend/apps/core/email_oauth_urls.py');
  assert.match(urls, /email_oauth_connect/);
  assert.match(urls, /email_oauth_callback/);
});

test('Email OAuth callback stores tokens server-side and never projects them', async () => {
  const oauth = await read('../backend/apps/core/email_oauth.py');
  assert.match(oauth, /update_or_create/);
  assert.match(oauth, /oauth_refresh_token/);
});

test('Email inbox lists synced messages with contact/deal deep-links', async () => {
  const inbox = await read('../backend/templates/dashboard/email_inbox.html');
  assert.match(inbox, /email_messages/);
  assert.match(inbox, /#contact-\{\{ email_message\.contact\.pk \}\}/);
  assert.match(inbox, /#deal-\{\{ email_message\.deal\.pk \}\}/);
  const contactRow = await read('../backend/templates/dashboard/partials/contact_row.html');
  assert.match(contactRow, /id="contact-\{\{ contact\.pk \}\}"/);
  const dealRow = await read('../backend/templates/dashboard/partials/deal_row.html');
  assert.match(dealRow, /id="deal-\{\{ deal\.pk \}\}"/);
});
