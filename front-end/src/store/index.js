import Vuex from 'vuex'

import user from './modules/user'
import menu from './modules/menu'

const store = new Vuex.Store({
  modules: {
    user,
    menu
  }
})

export default store
