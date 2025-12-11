export const getToken = () => {
    // 从 cookie 中获取 token
    const cookies = document.cookie.split(';')
    const tokenCookie = cookies.find((cookie) => cookie.trim().startsWith('ai_mark_token='))

    if (tokenCookie) {
        return tokenCookie.split('=')[1].trim()
    }

    return null
}

export const apiClient = {
    request: async (url: string, options: RequestInit = {}) => {
        const token = getToken()
        const headers = new Headers(options.headers)

        if (token) {
            headers.set('Authorization', `${token}`)
        }

        // Ensure Content-Type is set if body is present and not FormData
        if (options.body && typeof options.body === 'string' && !headers.has('Content-Type')) {
            headers.set('Content-Type', 'application/json')
        }

        const config: RequestInit = {
            ...options,
            headers,
        }

        return fetch(url, config)
    },
    get: (url: string, options: RequestInit = {}) => {
        return apiClient.request(url, { ...options, method: 'GET' })
    },
    post: (url: string, body?: any, options: RequestInit = {}) => {
        const isFormData = body instanceof FormData
        return apiClient.request(url, {
            ...options,
            method: 'POST',
            body: isFormData ? body : JSON.stringify(body),
        })
    },
    put: (url: string, body?: any, options: RequestInit = {}) => {
        const isFormData = body instanceof FormData
        return apiClient.request(url, {
            ...options,
            method: 'PUT',
            body: isFormData ? body : JSON.stringify(body),
        })
    },
    delete: (url: string, options: RequestInit = {}) => {
        return apiClient.request(url, { ...options, method: 'DELETE' })
    },
}
