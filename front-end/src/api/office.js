import request from '@/utils/request'

/**
 * 在线文档列表
 */
export function getDocumentList(params) {
  return request({
    url: '/api/office/documents/',
    method: 'get',
    params,
  })
}

/**
 * 获取文档详情
 */
export function getDocumentDetail(id) {
  return request({
    url: `/api/office/documents/${id}/`,
    method: 'get',
  })
}

/**
 * 创建文档
 */
export function createDocument(data) {
  return request({
    url: '/api/office/documents/',
    method: 'post',
    data,
  })
}

/**
 * 更新文档
 */
export function updateDocument(id, data) {
  return request({
    url: `/api/office/documents/${id}/`,
    method: 'put',
    data,
  })
}

/**
 * 部分更新文档
 */
export function patchDocument(id, data) {
  return request({
    url: `/api/office/documents/${id}/`,
    method: 'patch',
    data,
  })
}

/**
 * 删除文档
 */
export function deleteDocument(id) {
  return request({
    url: `/api/office/documents/${id}/`,
    method: 'delete',
  })
}

/**
 * 置顶/取消置顶文档
 */
export function togglePinDocument(id) {
  return request({
    url: `/api/office/documents/${id}/toggle_pin/`,
    method: 'post',
  })
}


