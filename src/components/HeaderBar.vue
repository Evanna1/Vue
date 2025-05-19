<template>
  <header class="header-bar">
    <router-link to="/" class="logo">NexTecht</router-link>

    <div class="center-group">
      <router-link
        v-if="isLoggedIn"
        to="/create"
        class="write-btn shifted-left"
      >+创作</router-link>
    </div>

    <div class="header-actions shifted-left-actions">
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
const showDropdown = ref(false)
let hideTimer: number | null = null

onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    isLoggedIn.value = true
    avatarUrl.value = localStorage.getItem('avatar') || '/default-avatar.png'
  }
})

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
  position: fixed; /* 使用 fixed 定位 */
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
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
  justify-content: flex-end; /* 保持靠右对齐 */
  gap: 20px;
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

.shifted-left {
  margin-right: 150px; /* 调整这个值来控制 "+创作" 左移的距离 */
}

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

.shifted-left-actions {
  margin-right: 50px; /* 调整这个值来控制 "个人信息" 那一栏左移的距离 */
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