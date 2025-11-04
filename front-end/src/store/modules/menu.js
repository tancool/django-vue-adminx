import { getMenuTree } from "@/api/menu"

const state = {
  menuTree: [],
}

const mutations = {
  SET_MENU_TREE: (state, menuTree) => {
    state.menuTree = menuTree
  },
}

const actions = {
  /**
   * 获取菜单树
   * @returns {Promise<boolean>} 获取是否成功
   */
  async getMenuTree({ commit }) {
    try {
      const res = await getMenuTree()
      commit('SET_MENU_TREE', res || [])
      return true
    } catch (e) {
      console.error('获取菜单树失败:', e)
      commit('SET_MENU_TREE', [])
      return false
    }
  },
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}

