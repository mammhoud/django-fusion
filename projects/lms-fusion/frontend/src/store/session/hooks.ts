'use client';

import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { hydrateFromCookieHeader, selectSession } from './sessionSlice';

export function useRequestSession() {
  const dispatch = useAppDispatch();
  const session = useAppSelector(selectSession);

  useEffect(() => {
    if (!session.hydrated && typeof document !== 'undefined') {
      dispatch(hydrateFromCookieHeader(document.cookie));
    }
  }, [dispatch, session.hydrated]);

  return session;
}
