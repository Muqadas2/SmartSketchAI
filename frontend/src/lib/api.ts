import { API_BASE_URL } from '../config';
import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
} from './authStore';

type RequestOptions = RequestInit & {
  body?: Record<string, unknown> | string;
  skipAuth?: boolean;
};

/**
 * Call the refresh endpoint and return the new access token, or null if refresh fails.
 */
async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  const res = await fetch(`${API_BASE_URL}/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  });

  if (!res.ok) return null;
  const data = (await res.json()) as { access: string };
  setTokens(data.access, refresh);
  return data.access;
}

/**
 * Redirect to login when session is invalid (e.g. refresh failed).
 */
function redirectToLogin(): void {
  clearTokens();
  window.location.href = '/login';
}

/**
 * API request with:
 * - Base URL prefix
 * - JSON body/headers when body is an object
 * - Authorization: Bearer <access> for protected calls (unless skipAuth)
 * - On 401: try refresh once, retry request; if refresh fails, redirect to login
 */
export async function request<T = unknown>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { body, skipAuth = false, headers = {}, ...init } = options;

  const url = path.startsWith('http') ? path : `${API_BASE_URL.replace(/\/$/, '')}/${path.replace(/^\//, '')}`;
  const reqHeaders: HeadersInit = {
    ...(typeof headers === 'object' && !(headers instanceof Headers)
      ? headers
      : {}),
  } as Record<string, string>;

  if (body !== undefined) {
    reqHeaders['Content-Type'] = 'application/json';
  }
  if (!skipAuth) {
    const access = getAccessToken();
    if (access) reqHeaders['Authorization'] = `Bearer ${access}`;
  }

  let res = await fetch(url, {
    ...init,
    headers: reqHeaders,
    body:
      body === undefined
        ? undefined
        : typeof body === 'string'
          ? body
          : JSON.stringify(body),
  });

  if (res.status === 401 && !skipAuth) {
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      reqHeaders['Authorization'] = `Bearer ${newAccess}`;
      res = await fetch(url, {
        ...init,
        headers: reqHeaders,
        body:
          body === undefined
            ? undefined
            : typeof body === 'string'
              ? body
              : JSON.stringify(body),
      });
    }
    if (res.status === 401) {
      redirectToLogin();
      throw new Error('Unauthorized');
    }
  }

  if (!res.ok) {
    let message = res.statusText;
    try {
      const data = (await res.json()) as { error?: string; detail?: string };
      message = data.error ?? data.detail ?? message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }

  const contentType = res.headers.get('content-type');
  if (contentType?.includes('application/json')) {
    return res.json() as Promise<T>;
  }
  return undefined as T;
}

/** POST /api/token/ - login, no auth */
export async function loginWithToken(username: string, password: string) {
  return request<{ access: string; refresh: string }>('token/', {
    method: 'POST',
    body: { username, password },
    skipAuth: true,
  });
}

/** POST /api/token/refresh/ - refresh, no auth */
export async function refreshToken() {
  const refresh = getRefreshToken();
  if (!refresh) throw new Error('No refresh token');
  return request<{ access: string }>('token/refresh/', {
    method: 'POST',
    body: { refresh },
    skipAuth: true,
  });
}

/** POST /api/register/ - register, no auth */
export async function registerUser(body: {
  username: string;
  email: string;
  password: string;
  role?: string;
}) {
  return request<unknown>('register/', {
    method: 'POST',
    body: { ...body, role: body.role ?? 'general' },
    skipAuth: true,
  });
}

/** POST /api/forensic/generate/ */
export async function generateForensicSketch(body: {
  prompt: string;
  case_type?: string;
  age?: number | null;
}) {
  return request<any>('forensic/generate/', {
    method: 'POST',
    body,
  });
}

/** POST /api/forensic/edit/ */
export async function editForensicSketch(body: {
  original_image_id: number;
  edit_prompt: string;
  strength?: number;
}) {
  return request<any>('forensic/edit/', {
    method: 'POST',
    body,
  });
}

/** GET /api/my-images/ */
export async function fetchUserImages() {
  return request<any[]>('my-images/', {
    method: 'GET',
  });
}
