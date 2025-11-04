import request from '@/utils/request'

/**
 * 文件上传接口
 * @param {File} file - 要上传的文件
 * @returns {Promise} 返回 { url, filename, original_name, size }
 */
export function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request({
    url: '/api/common/upload/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

