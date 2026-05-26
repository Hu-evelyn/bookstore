// src/utils/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000', // FastAPI 后端地址
  timeout: 5000
})

// 请求拦截器：自动在请求头里带上 Token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['token'] = token
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器：统一处理报错信息
request.interceptors.response.use(
  response => response.data,
  error => {
    const msg = error.response?.data?.detail || '网络请求错误'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default request