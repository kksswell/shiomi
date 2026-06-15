const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');

export class ApiError extends Error {
  public status: number;
  public payload: unknown;

  constructor(message: string, status: number, payload: unknown = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.payload = payload;
  }
}

interface ApiFetchOptions extends RequestInit {
  timeoutMs?: number;
}

export function authUrl(path: string): string {
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { timeoutMs = 8000, ...requestOptions } = options;
  const headers = new Headers(requestOptions.headers || {});
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);

  if (requestOptions.body && !(requestOptions.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  try {
    const response = await fetch(authUrl(path), {
      ...requestOptions,
      credentials: 'include',
      headers,
      signal: controller.signal,
    });

    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json') ? await response.json() : await response.text();

    if (!response.ok) {
      const message = typeof payload === 'object' && payload && 'detail' in payload
        ? String((payload as { detail: string }).detail)
        : `Ошибка запроса: ${response.status}`;
      throw new ApiError(message, response.status, payload);
    }

    return payload as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('Превышено время ожидания ответа сервера', 408);
    }
    throw error;
  } finally {
    window.clearTimeout(timer);
  }
}
