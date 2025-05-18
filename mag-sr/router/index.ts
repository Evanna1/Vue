import { createRouter, createWebHistory } from 'vue-router'
import AdminLogin from '../views/AdminLogin.vue'
import Dashboard from '../views/Dashboard.vue'
import ArticleDetail from '../components/ArticleDetail.vue'
import FollowView from '../components/FollowView.vue'
import PostDetail from '../components/PostDetail.vue'
import OtherUserProfile from '../components/OtherUserProfile.vue'
import UserProfile from '../components/UserProfile.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: AdminLogin },
  { path: '/bashbord', component:Dashboard }, // ✅ 管理员后台页面
  { path: '/article-detail/:articleId',component: ArticleDetail },
  { path: '/follow', component: FollowView, meta: { requiresAuth: true } },
  { path: '/post/:id', component:PostDetail},
  { path: '/user/:userId', name: 'OtherUserProfile', component: OtherUserProfile},
  { path: '/user/:userId', name: 'UserProfile', component: UserProfile }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
