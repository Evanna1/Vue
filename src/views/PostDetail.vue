<template>
  <router-link to="/" class="logo-absolute">NexTecht</router-link>
  <div class="post-detail-container">
    <!-- 标题卡片 -->
    <div class="card title-card">
      <h1 class="post-title">{{ post.title }}</h1>
    </div>

    <!-- 正文卡片 -->
    <div class="card content-card">
      <div class="post-content" v-html="post.content"></div>
    </div>
  </div>
</template>



<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const post = ref({ title: '', content: '' })
const route = useRoute()
const router = useRouter()

onMounted(async () => {
  const postId = route.params.id
  try {
    const response = await axios.get(`http://127.0.0.1:5000/user/article_content/${postId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('jwt_token')}`,
      },
    })
    post.value = response.data.article
  } catch (error) {
    console.error('Error fetching post details:', error)
  }
})

function goBack() {
  router.push('/profile')
}
</script>



<style scoped>
.logo-absolute {
  position: absolute;
  top: 20px;
  left: 30px;
  font-family: 'Great Vibes', cursive;
  font-size: 42px;
  font-weight: bold;
  color: #0077cc;
  text-decoration: none;
  z-index: 1000;
}
.post-detail-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
  font-family: 'Helvetica Neue', sans-serif;
}

.card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  padding: 30px;
  margin-bottom: 30px;
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.title-card {
  text-align: center;
}

.post-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
}

.content-card {
  line-height: 1.7;
  font-size: 16px;
  color: #333;
}

.post-content >>> blockquote {
  margin-left: 0;
  padding-left: 1em;
  border-left: 4px solid #ccc;
  color: #555;
  font-style: italic;
}
</style>

