"""Supabase client factory."""

from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from shared.config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """Return a cached Supabase client using the service-role key."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)


def get_supabase_anon_client() -> Client:
    """Return a Supabase client using the anon (public) key.

    Useful when proxying requests on behalf of end-users so that RLS
    policies are enforced.
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)
