<template>
  <header class="header-bar">
    <router-link to="/" class="logo">NexTecht</router-link>

    <div class="center-group">
      <div class="search-box">
        <input v-model="keyword" placeholder="搜索用户、标题或内容" />
        <button @click="handleSearch">
          <i class="icon-search"></i>
        </button>
      </div>

      <router-link
        v-if="isLoggedIn"
        to="/create"
        class="write-btn"
      >+创作</router-link>
    </div>

    <div class="header-actions">
      <div v-if="!isLoggedIn" class="action-group">
        <button @click="goLogin">登录 / 注册</button>
      </div>
      <div v-else class="logged-in-group">
        <div
          class="avatar-container dropdown-wrapper"
          @mouseenter="onMouseEnter"
          @mouseleave="onMouseLeave"
        >
          <img class="avatar" :src="avatarUrl" />
          <div v-if="showDropdown" class="dropdown-menu">
            <router-link to="/profile">个人中心</router-link>
            <router-link to="/settings">设置</router-link>
            <div @click="logout">退出</div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>


<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoggedIn = ref(false)
const avatarUrl = ref('/default-avatar.png')
const keyword = ref('')
const showDropdown = ref(false)
let hideTimer: number | null = null

onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    isLoggedIn.value = true
    avatarUrl.value = localStorage.getItem('avatar') || '/default-avatar.png'
  }
})

function handleSearch() {
  console.log('搜索关键词：', keyword.value)
}

function goLogin() {
  router.push('/login')
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('avatar')
  localStorage.removeItem('user_id')
  isLoggedIn.value = false
  router.push('/')
}

function onMouseEnter() {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
  showDropdown.value = true
}

function onMouseLeave() {
  hideTimer = window.setTimeout(() => {
    showDropdown.value = false
  }, 200)
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 30px;
  background: linear-gradient(to right, #dfe9f3, #ffffff);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 10;
}

.logo {
  font-family: 'Great Vibes', cursive;
  font-size: 28px;
  font-weight: bold;
  color: #0077cc;
  text-decoration: none;
}

.center-group {
  display: flex;
  align-items: center;
  flex: 1;
  justify-content: center;
  gap: 20px;
  margin: 0 40px;
}

.search-box {
  display: flex;
  max-width: 500px;
  width: 100%;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 30px;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}

.search-box input {
  flex: 1;
  padding: 10px 16px;
  border: none;
  font-size: 14px;
  outline: none;
}

.search-box button {
  background: transparent;
  border: none;
  padding: 0 16px;
  cursor: pointer;
  color: #555;
}

.search-box:hover {
  box-shadow: 0 0 8px rgba(0, 123, 255, 0.2);
}

/* 🔍 搜索按钮图标 */
.icon-search::before {
  content: '🔍';
  font-size: 18px;
}

.write-btn {
  padding: 6px 14px;
  background: linear-gradient(to right, #56ccf2, #2f80ed);
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.write-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.15);
}

/* ✅ 登录 / 注册 按钮 样式 */
.action-group button {
  padding: 6px 14px;
  background: linear-gradient(to right, #56ccf2, #2f80ed);
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.action-group button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.15);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-container {
  position: relative;
  cursor: pointer;
  display: flex;
  align-items: center;
  margin-top: 5px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #eee;
}

.dropdown-wrapper {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  min-width: 120px;
  z-index: 100;
}

.dropdown-menu a,
.dropdown-menu div {
  font-size: 14px;
  color: #333;
  text-decoration: none;
  cursor: pointer;
}

.dropdown-menu div:hover {
  color: #007bff;
}



</style>
