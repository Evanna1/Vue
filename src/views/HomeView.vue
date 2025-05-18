<template>
  <div class="home-container">
    <HeaderBar @search="handleSearch" :initialKeyword="keyword" />
    <div class="tabs">
      <button :class="{ active: activeTab === 'recommend' }" @click="setActiveTab('recommend')">
        推荐
      </button>
      <button :class="{ active: activeTab === 'follow' }" @click="setActiveTab('follow')">
        关注
      </button>
      <button :class="{ active: activeTab === 'hot' }" @click="setActiveTab('hot')">热榜</button>
    </div>

    <div v-if="isLoading" class="loading-message">正在加载文章...</div>
    <div v-else-if="filteredPosts.length === 0 && keyword" class="no-results-message">
      没有找到与 "{{ keyword }}"相关的文章。
    </div>
    <div v-else-if="filteredPosts.length === 0 && activeTab !== 'recommend'" class="no-results-message">
      此分类下暂无文章。
    </div>
    <div class="post-list" v-else>
      <div class="post-card" v-for="post in filteredPosts" :key="post.id" @click="goToPost(post.id)">
        <h3>{{ post.title }}</h3>
        <p class="author">作者：{{ post.user?.username || post.authorName || '未知作者' }}</p>
        <p class="content">{{ getExcerpt(post.content) }}</p>
        <div v-if="post.tags && post.tags.length > 0" class="post-tags">
          <span v-for="tag in post.tags" :key="tag" class="tag-item" @click.stop="searchByTag(tag)">
            {{ tag }}
          </span>
        </div>
        <p v-if="activeTab === 'recommend' && post.score" class="recommend-score">推荐度：{{ post.score }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HeaderBar from '@/components/HeaderBar.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

type TabType = 'recommend' | 'follow' | 'hot';
const activeTab = ref<TabType>('recommend')
const keyword = ref('')
const isLoading = ref(false)

interface User {
  id: number;
  username: string;
  avatar?: string;
}

interface RecommendationItem {
  article_id: number;
  title: string;
  score: number;
}

interface Post {
  id: number;
  userId: number;
  title: string;
  content: string;
  tags?: string[];
  user?: User;
  authorName?: string;
  createdAt: string;
  views?: number;
  likes?: number;
  score?: number; // 用于存储推荐度分数
}

const allPosts = ref<Post[]>([])

const fetchPosts = async () => {
  isLoading.value = true
  console.log(`Fetching posts for tab: ${activeTab.value}, keyword: ${keyword.value}`)
  try {
    let url = '';
    const headers: any = {};
    const params: any = {};
    const token = localStorage.getItem('token');
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    if (activeTab.value === 'recommend') {
      url = 'http://127.0.0.1:5000/article/recommend';
      if (keyword.value) {
        params.keyword = keyword.value;
      }
    } else if (activeTab.value === 'follow') {
      url = 'http://127.0.0.1:5000/following'; // 修正关注接口地址
    } else if (activeTab.value === 'hot') {
      url = 'http://127.0.0.1:5000/article/hot';
    } else if (keyword.value) {
      url = 'http://127.0.0.1:5000/article/search';
      params.keyword = keyword.value;
    }

    if (url) {
      const response = await axios.get(url, { headers, params });
      if (response.data && response.data.state === 1) {
        if (activeTab.value === 'recommend' && Array.isArray(response.data.recommendations)) {
          // 处理推荐接口返回的数据，并直接包含文章详细信息
          allPosts.value = response.data.recommendations.map((item: any) => ({
            id: item.article_id,
            userId: item.userId,
            title: item.title,
            content: item.content,
            tags: item.tags || [],
            user: item.user,
            authorName: item.authorName,
            createdAt: item.createdAt,
            views: item.views,
            likes: item.likes,
            score: item.score,
          } as Post));
        } else if (Array.isArray(response.data.data)) {
          allPosts.value = response.data.data.map((post: any) => ({
            ...post,
            tags: post.tag ? post.tag.split(/,|，/).map((t: string) => t.trim()).filter((t:string) => t) : []
          }));
        } else if (Array.isArray(response.data)) {
          allPosts.value = response.data.map((post: any) => ({
            ...post,
            tags: post.tag ? post.tag.split(/,|，/).map((t: string) => t.trim()).filter((t:string) => t) : []
          }));
        } else {
          allPosts.value = [];
          console.warn("No posts data found or in unexpected format", response.data);
        }
      } else {
        allPosts.value = [];
        console.warn("Fetch posts failed", response.data);
      }
    } else {
      allPosts.value = [];
    }
  } catch (error) {
    console.error('Error fetching posts:', error)
    allPosts.value = [];
  } finally {
    isLoading.value = false
  }
}

const filteredPosts = computed(() => {
  let listToFilter = [...allPosts.value]

  if (!keyword.value) {
    return listToFilter
  }

  const searchTerm = keyword.value.toLowerCase()
  return listToFilter.filter(post =>
    (post.title && post.title.toLowerCase().includes(searchTerm)) ||
    (post.content && post.content.toLowerCase().includes(searchTerm)) ||
    (post.user?.username && post.user.username.toLowerCase().includes(searchTerm)) ||
    (post.authorName && post.authorName.toLowerCase().includes(searchTerm)) ||
    (post.tags && post.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
  )
})

const handleSearch = (newKeyword: string) => {
  router.push({ query: newKeyword ? { search: newKeyword } : {} })
}

watch(() => route.query.search, (newSearchTerm) => {
  const term = Array.isArray(newSearchTerm) ? newSearchTerm[0] : newSearchTerm
  keyword.value = term || ''
  fetchPosts() // 搜索时重新获取数据
}, { immediate: true })

watch(activeTab, () => {
  if (keyword.value && activeTab.value !== 'recommend') {
    keyword.value = '';
    router.push({ query: {} });
  }
  fetchPosts()
})

onMounted(() => {
  fetchPosts() // 初始加载数据
})

function setActiveTab(tab: TabType) {
  activeTab.value = tab
}

function goToPost(id: number | string) {
  router.push(`/post/${id}`)
}

function getExcerpt(content: string, length: number = 100): string {
  if (!content) return '暂无内容预览...'
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = content
  const text = tempDiv.textContent || tempDiv.innerText || ''
  return text.length > length ? text.slice(0, length) + '...' : text
}

function searchByTag(tag: string) {
  if (!tag) return
  router.push({ query: { search: tag } })
}
</script>

<style scoped>
.home-container {
  padding: 0;
  background: #f9f9f9;
  min-height: 100vh;
  padding-top: 60px; /* Adjust if HeaderBar has a fixed height */
}

.tabs {
  display: flex;
  justify-content: center;
  margin: 20px 0;
  padding: 0 10px; /* Add some padding for smaller screens */
  flex-wrap: wrap; /* Allow tabs to wrap on small screens */
}

.tabs button {
  padding: 10px 20px; /* Increased padding */
  margin: 5px; /* Adjusted margin for wrapping */
  background: #e9ecef; /* Lighter background */
  border: none;
  cursor: pointer;
  border-radius: 20px; /* Pill shape */
  font-size: 16px; /* Slightly larger font */
  color: #495057;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.tabs button:hover {
  background: #ced4da;
}

.tabs button.active {
  background: #007bff;
  color: white;
  font-weight: bold;
}

.post-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 16px 20px; /* Add bottom padding */
}

.post-card {
  background: white;
  padding: 20px; /* Increased padding */
  border-radius: 12px; /* More rounded corners */
  margin-bottom: 20px; /* Increased margin */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* Softer shadow */
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}
.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}


.post-card h3 {
  margin: 0 0 8px 0; /* Add bottom margin */
  font-size: 22px; /* Larger title */
  color: #343a40;
}

.post-card .author {
  color: #6c757d; /* Softer author text color */
  font-size: 14px;
  margin: 0 0 12px 0; /* Add bottom margin */
}

.post-card .content {
  font-size: 16px;
  color: #495057;
  line-height: 1.7; /* Improved readability */
  margin-bottom: 15px;
}

.loading-message, .no-results-message {
  text-align: center;
  padding: 40px 20px;
  font-size: 18px;
  color: #6c757d;
}
.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.tag-item {
  background-color: #f0f0f0;
  color: #555;
  padding: 4px 10px;
  border-radius: 15px; /* More rounded tags */
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
}
.tag-item:hover {
  background-color: #007bff;
  color: white;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .tabs button {
    padding: 8px 15px;
    font-size: 15px;
  }
  .post-card h3 {
    font-size: 20px;
  }
  .post-card .content {
    font-size: 15px;
  }
}
</style>