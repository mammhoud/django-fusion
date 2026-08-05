import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  FusionSessionSync,
  SESSION_SYNC_MIRROR_KEY,
} from './session-sync';

const tick = () => new Promise((resolve) => setTimeout(resolve, 25));

describe('FusionSessionSync — BroadcastChannel transport', () => {
  it('delivers a published preference to a subscribed instance', async () => {
    const sender = new FusionSessionSync('test-bc-deliver');
    const receiver = new FusionSessionSync('test-bc-deliver');
    const received: (boolean | null)[] = [];
    receiver.subscribe((value) => received.push(value));

    sender.publish(true);
    await tick();
    expect(received).toEqual([true]);

    sender.dispose();
    receiver.dispose();
  });

  it('round-trips false over BroadcastChannel', async () => {
    const sender = new FusionSessionSync('test-bc-false');
    const receiver = new FusionSessionSync('test-bc-false');
    const received: (boolean | null)[] = [];
    receiver.subscribe((value) => received.push(value));

    sender.publish(false);
    await tick();
    expect(received).toEqual([false]);

    sender.dispose();
    receiver.dispose();
  });

  it('round-trips null (cleared → default) over BroadcastChannel', async () => {
    const sender = new FusionSessionSync('test-bc-null');
    const receiver = new FusionSessionSync('test-bc-null');
    const received: (boolean | null)[] = [];
    receiver.subscribe((value) => received.push(value));

    sender.publish(null);
    await tick();
    expect(received).toEqual([null]);

    sender.dispose();
    receiver.dispose();
  });

  it('ignores messages on a different channel name', async () => {
    const sender = new FusionSessionSync('test-bc-a');
    const receiver = new FusionSessionSync('test-bc-b');
    const received: (boolean | null)[] = [];
    receiver.subscribe((value) => received.push(value));

    sender.publish(true);
    await tick();
    expect(received).toEqual([]);

    sender.dispose();
    receiver.dispose();
  });

  it('publishes without the sender ever subscribing (lazy channel)', async () => {
    // Regression: publish() used to no-op when the channel was only created
    // in subscribe(); ensureChannel() must be lazy for the sender too.
    const sender = new FusionSessionSync('test-bc-lazy');
    const receiver = new FusionSessionSync('test-bc-lazy');
    const received: (boolean | null)[] = [];
    receiver.subscribe((value) => received.push(value));

    // sender never subscribes — publish must still send the message
    sender.publish(true);
    await tick();
    expect(received).toEqual([true]);

    sender.dispose();
    receiver.dispose();
  });

  it('is inert after dispose (no publish, no new subscriptions)', async () => {
    const sender = new FusionSessionSync('test-bc-disposed');
    const receiver = new FusionSessionSync('test-bc-disposed');
    const received: (boolean | null)[] = [];
    receiver.subscribe((value) => received.push(value));

    sender.dispose();
    sender.publish(true); // must be a no-op, not a channel leak
    await tick();
    expect(received).toEqual([]);

    // a subscription made after dispose attaches nothing and hears nothing
    const late = new FusionSessionSync('test-bc-disposed-late');
    late.subscribe((value) => received.push(value));
    late.dispose();
    late.publish(null);
    await tick();
    expect(received).toEqual([]);

    receiver.dispose();
  });
});

describe('FusionSessionSync — storage-event fallback transport', () => {
  let listeners: Record<string, (event: unknown) => void>;
  let store: Record<string, string>;

  beforeEach(() => {
    listeners = {};
    store = {};
    // Force the fallback path: no BroadcastChannel, window + localStorage
    // available (browser-like environment).
    vi.stubGlobal('BroadcastChannel', undefined);
    vi.stubGlobal('window', {
      addEventListener: (type: string, cb: (event: unknown) => void) => {
        listeners[type] = cb;
      },
      removeEventListener: (type: string) => {
        delete listeners[type];
      },
    });
    vi.stubGlobal('localStorage', {
      setItem: (key: string, value: string) => {
        store[key] = value;
      },
      getItem: (key: string) => store[key] ?? null,
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('publishes the mirror payload with the expected format', () => {
    const sync = new FusionSessionSync('test-store-pub');
    sync.publish(false);
    expect(store[SESSION_SYNC_MIRROR_KEY]).toMatch(/^\d+:false$/);
    sync.dispose();
  });

  it('applies a mirror change via the storage event', () => {
    const sync = new FusionSessionSync('test-store-app');
    const received: (boolean | null)[] = [];
    sync.subscribe((value) => received.push(value));

    // another tab writes the mirror → storage event fires here
    store[SESSION_SYNC_MIRROR_KEY] = '1700000000000:true';
    listeners.storage?.({
      key: SESSION_SYNC_MIRROR_KEY,
      newValue: '1700000000000:true',
    });
    expect(received).toEqual([true]);
    sync.dispose();
  });

  it('applies a cleared (null) mirror change', () => {
    const sync = new FusionSessionSync('test-store-null');
    const received: (boolean | null)[] = [];
    sync.subscribe((value) => received.push(value));

    store[SESSION_SYNC_MIRROR_KEY] = '1700000000001:null';
    listeners.storage?.({
      key: SESSION_SYNC_MIRROR_KEY,
      newValue: '1700000000001:null',
    });
    expect(received).toEqual([null]);
    sync.dispose();
  });

  it('ignores storage events for unrelated keys', () => {
    const sync = new FusionSessionSync('test-store-other');
    const received: (boolean | null)[] = [];
    sync.subscribe((value) => received.push(value));

    listeners.storage?.({
      key: 'some-other-key',
      newValue: '1700000000002:true',
    });
    expect(received).toEqual([]);
    sync.dispose();
  });
});

describe('FusionSessionSync — dedupe (last-writer-wins by timestamp)', () => {
  let listeners: Record<string, (event: unknown) => void>;

  beforeEach(() => {
    listeners = {};
    vi.stubGlobal('BroadcastChannel', undefined);
    vi.stubGlobal('window', {
      addEventListener: (type: string, cb: (event: unknown) => void) => {
        listeners[type] = cb;
      },
      removeEventListener: (type: string) => {
        delete listeners[type];
      },
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function emit(sync: FusionSessionSync, newValue: string): void {
    listeners.storage?.({ key: SESSION_SYNC_MIRROR_KEY, newValue });
  }

  it('applies the same timestamped change only once', () => {
    const sync = new FusionSessionSync('test-dedupe');
    const received: (boolean | null)[] = [];
    sync.subscribe((value) => received.push(value));

    // identical change delivered twice (e.g. BC + storage fallback)
    emit(sync, '1700000000100:true');
    emit(sync, '1700000000100:true');
    expect(received).toEqual([true]);
    sync.dispose();
  });

  it('ignores an older timestamp arriving after a newer one', () => {
    const sync = new FusionSessionSync('test-stale');
    const received: (boolean | null)[] = [];
    sync.subscribe((value) => received.push(value));

    emit(sync, '1700000000100:true');
    emit(sync, '1700000000000:false'); // stale → ignored
    expect(received).toEqual([true]);
    sync.dispose();
  });

  it('applies distinct timestamps in order', () => {
    const sync = new FusionSessionSync('test-order');
    const received: (boolean | null)[] = [];
    sync.subscribe((value) => received.push(value));

    emit(sync, '1700000000100:true');
    emit(sync, '1700000000200:null');
    expect(received).toEqual([true, null]);
    sync.dispose();
  });
});
