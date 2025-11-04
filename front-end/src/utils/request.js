import axios from 'axios'
import { Message } from '@arco-design/web-vue'

// 支持 Cookie（Session 认证需要）
const service = axios.create({
  baseURL: import.meta.env.VITE_HOST || 'http://127.0.0.1:8000',
  withCredentials: true, // 支持跨域 Cookie
  timeout: 10000,
})

// 获取 CSRF token（从 Cookie 中读取）
function getCsrfToken() {
  const name = 'csrftoken'
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    const [key, value] = cookie.trim().split('=')
    if (key === name) {
      return decodeURIComponent(value)
    }
  }
  return null
}

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 对于需要 CSRF token 的请求（POST, PUT, DELETE, PATCH），添加 CSRF token
    const method = config.method?.toUpperCase()
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
      const csrfToken = getCsrfToken()
      
      // 在请求头中添加 CSRF token
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken
      } else {
        console.warn('CSRF token 未找到，请确保已登录')
      }
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data

    // 如果后端返回的状态码不是 200-299，视为错误
    if (response.status >= 400) {
      Message.error(res.detail || res.message || '请求失败')
      return Promise.reject(new Error(res.detail || res.message || 'Error'))
    }

    return res
  },
  error => {
    // 处理错误响应
    const errorMessage = error.response?.data?.detail || 
                         error.response?.data?.message || 
                         error.message || 
                         '请求失败'
    
    Message.error(errorMessage)
    return Promise.reject(error)
  }
)

export default service
