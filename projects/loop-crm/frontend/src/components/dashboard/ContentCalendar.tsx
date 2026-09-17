import type { FormEvent } from 'react';
import { useEffect, useMemo, useState } from 'react';

interface Post {
  id: number;
  content: string;
  scheduled_at: string;
  status: string;
  channel_id: number;
  campaign_id?: number | null;
}

interface Option { id: number; name?: string; account_name?: string; platform?: string; }

const API = '/apis/core/resources';

function csrfToken(): string {
  return document.cookie.match(/(?:^|; )csrftoken=([^;]*)/)?.[1] ?? '';
}

function localDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, { weekday: 'short', month: 'short', day: 'numeric' }).format(new Date(value));
}

export default function ContentCalendar() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [channels, setChannels] = useState<Option[]>([]);
  const [campaigns, setCampaigns] = useState<Option[]>([]);
  const [status, setStatus] = useState('all');
  const [editing, setEditing] = useState<number | null>(null);
  const [content, setContent] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [channelId, setChannelId] = useState('');
  const [campaignId, setCampaignId] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  const load = async () => {
    const [postResponse, channelResponse, campaignResponse] = await Promise.all([
      fetch(`${API}/posts/`, { credentials: 'include' }),
      fetch(`${API}/channels/`, { credentials: 'include' }),
      fetch(`${API}/campaigns/`, { credentials: 'include' }),
    ]);
    if (!postResponse.ok) throw new Error('Content calendar unavailable.');
    const postPayload = await postResponse.json();
    setPosts(postPayload.results ?? []);
    if (channelResponse.ok) setChannels((await channelResponse.json()).results ?? []);
    if (campaignResponse.ok) setCampaigns((await campaignResponse.json()).results ?? []);
  };

  useEffect(() => { void load().catch((error) => setMessage(error instanceof Error ? error.message : 'Calendar unavailable.')); }, []);

  const visiblePosts = useMemo(() => posts
    .filter((post) => status === 'all' || post.status === status)
    .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime()), [posts, status]);

  const resetForm = () => {
    setEditing(null); setContent(''); setScheduledAt(''); setChannelId(''); setCampaignId('');
  };

  const save = async (event: FormEvent) => {
    event.preventDefault();
    if (!content.trim() || !scheduledAt || !channelId) return setMessage('Content, channel, and schedule are required.');
    setBusy(true); setMessage('');
    try {
      const payload = { content: content.trim(), scheduled_at: new Date(scheduledAt).toISOString(), channel_id: Number(channelId), campaign_id: campaignId ? Number(campaignId) : null };
      const response = await fetch(editing ? `${API}/posts/${editing}/` : `${API}/posts/`, {
        method: editing ? 'PATCH' : 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error('Post could not be saved.');
      await load(); resetForm(); setMessage(editing ? 'Post updated.' : 'Post added to the calendar.');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Post could not be saved.'); }
    finally { setBusy(false); }
  };

  const remove = async (id: number) => {
    setBusy(true); setMessage('');
    try {
      const response = await fetch(`${API}/posts/${id}/`, { method: 'DELETE', credentials: 'include', headers: { 'X-CSRFToken': csrfToken() } });
      if (!response.ok) throw new Error('Post could not be deleted.');
      setPosts((current) => current.filter((post) => post.id !== id));
      if (editing === id) resetForm();
      setMessage('Post deleted.');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Post could not be deleted.'); }
    finally { setBusy(false); }
  };

  const edit = (post: Post) => {
    setEditing(post.id); setContent(post.content); setScheduledAt(post.scheduled_at.slice(0, 16)); setChannelId(String(post.channel_id)); setCampaignId(post.campaign_id ? String(post.campaign_id) : '');
  };

  return (
    <section className="loop-calendar" data-calendar-surface="posts" aria-label="Content calendar">
      <div className="loop-calendar__toolbar">
        <div><span className="loop-calendar__kicker">LIVE CONTENT LEDGER</span><strong>{visiblePosts.length} scheduled record{visiblePosts.length === 1 ? '' : 's'}</strong></div>
        <label htmlFor="calendar-status">Filter<select id="calendar-status" value={status} onChange={(event) => setStatus(event.target.value)}><option value="all">All statuses</option>{['draft', 'pending_approval', 'approved', 'scheduled', 'published', 'failed'].map((item) => <option value={item} key={item}>{item.replace('_', ' ')}</option>)}</select></label>
      </div>
      <div className="loop-calendar__layout">
        <form className="loop-calendar__editor" data-calendar-editor onSubmit={(event) => void save(event)}>
          <span className="loop-calendar__kicker">{editing ? 'EDIT POST' : 'ADD POST'}</span>
          <h2>{editing ? 'Update scheduled content' : 'Schedule content'}</h2>
          <label htmlFor="calendar-content">Content<textarea id="calendar-content" value={content} maxLength={5000} rows={5} onChange={(event) => setContent(event.target.value)} /></label>
          <label htmlFor="calendar-channel">Channel<select id="calendar-channel" value={channelId} onChange={(event) => setChannelId(event.target.value)}><option value="">Choose channel</option>{channels.map((item) => <option value={item.id} key={item.id}>{item.platform} · {item.account_name}</option>)}</select></label>
          <label htmlFor="calendar-campaign">Campaign<select id="calendar-campaign" value={campaignId} onChange={(event) => setCampaignId(event.target.value)}><option value="">No campaign</option>{campaigns.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}</select></label>
          <label htmlFor="calendar-date">Scheduled for<input id="calendar-date" type="datetime-local" value={scheduledAt} onChange={(event) => setScheduledAt(event.target.value)} /></label>
          <div className="loop-calendar__actions"><button className="loop-button loop-button--primary" disabled={busy} type="submit">{busy ? 'Saving…' : editing ? 'Save changes →' : 'Add to calendar →'}</button>{editing && <button className="loop-button loop-button--quiet" type="button" onClick={resetForm}>Cancel</button>}</div>
        </form>
        <div className="loop-calendar__days">
          {visiblePosts.length === 0 ? <div className="loop-calendar__empty"><strong>No posts match this filter.</strong><p>Create a draft or choose another status.</p></div> : visiblePosts.map((post) => <article className="loop-calendar__post" key={post.id} data-post-id={post.id}><div><span className="loop-calendar__date">{localDate(post.scheduled_at)}</span><span className={`loop-calendar__status loop-calendar__status--${post.status}`}>{post.status.replace('_', ' ')}</span></div><p>{post.content}</p><small>{channels.find((channel) => channel.id === post.channel_id)?.account_name ?? `Channel ${post.channel_id}`}</small><div className="loop-calendar__post-actions"><button type="button" onClick={() => edit(post)}>Edit</button><button type="button" onClick={() => void remove(post.id)}>Delete</button></div></article>)}
        </div>
      </div>
      {message && <p className="loop-calendar__message" role="status">{message}</p>}
    </section>
  );
}
