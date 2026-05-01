import axios from 'axios'

function isSuspiciousLatinCharacter(character: string) {
  const code = character.codePointAt(0) ?? 0
  return code >= 0x00c0 && code <= 0x024f
}

function hasCjkCharacter(value: string) {
  return Array.from(value).some((character) => {
    const code = character.codePointAt(0) ?? 0
    return code >= 0x3400 && code <= 0x9fff
  })
}

function countSuspiciousCharacters(value: string) {
  return Array.from(value).filter(isSuspiciousLatinCharacter).length
}

function maybeDecodeMojibake(value: string) {
  if (!value || hasCjkCharacter(value) || countSuspiciousCharacters(value) === 0) {
    return value
  }

  const bytes = Uint8Array.from(Array.from(value), (character) => character.charCodeAt(0) & 0xff)
  const decoded = new TextDecoder('utf-8').decode(bytes)

  if (!decoded || decoded.includes('\uFFFD')) {
    return value
  }

  const originalScore = countSuspiciousCharacters(value)
  const decodedScore = countSuspiciousCharacters(decoded)
  return hasCjkCharacter(decoded) || decodedScore < originalScore ? decoded : value
}

function normalizePayload<T>(payload: T): T {
  if (typeof payload === 'string') {
    return maybeDecodeMojibake(payload) as T
  }
  if (Array.isArray(payload)) {
    return payload.map((item) => normalizePayload(item)) as T
  }
  if (payload && typeof payload === 'object') {
    return Object.fromEntries(Object.entries(payload).map(([key, value]) => [key, normalizePayload(value)])) as T
  }
  return payload
}

function extractDetailMessage(detail: unknown): string | null {
  if (typeof detail === 'string') {
    return maybeDecodeMojibake(detail)
  }
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (typeof item === 'string') {
          return maybeDecodeMojibake(item)
        }
        if (item && typeof item === 'object') {
          const location = Array.isArray((item as { loc?: unknown }).loc) ? ((item as { loc: unknown[] }).loc).join('.') : ''
          const message = typeof (item as { msg?: unknown }).msg === 'string' ? maybeDecodeMojibake((item as { msg: string }).msg) : ''
          return [location, message].filter(Boolean).join(': ')
        }
        return ''
      })
      .filter(Boolean)
    return parts.length > 0 ? parts.join('；') : null
  }
  if (detail && typeof detail === 'object') {
    const message = (detail as { message?: unknown }).message
    if (typeof message === 'string') {
      return maybeDecodeMojibake(message)
    }
  }
  return null
}

export function toErrorMessage(error: unknown, fallback = '请求失败，请稍后重试。') {
  if (axios.isAxiosError(error)) {
    const responseData = normalizePayload(error.response?.data)
    const detailMessage = extractDetailMessage(
      responseData && typeof responseData === 'object'
        ? (responseData as { detail?: unknown }).detail
        : responseData,
    )

    if (detailMessage) {
      return detailMessage
    }
    if (error.code === 'ECONNABORTED') {
      return '请求超时，请检查后端服务是否可用。'
    }
    if (!error.response) {
      return '无法连接到后端服务，请确认 API 服务已启动。'
    }
    return `请求失败（HTTP ${error.response.status}）。`
  }

  if (error instanceof Error) {
    return error.message || fallback
  }
  if (typeof error === 'string') {
    return error
  }
  return fallback
}

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 30000,
})

http.interceptors.response.use(
  (response) => {
    response.data = normalizePayload(response.data)
    return response
  },
  (error) => Promise.reject(error),
)

export default http
