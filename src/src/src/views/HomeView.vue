<template>
  <div class="home-container">
    <HeaderBar @search="handleSearch" :initialKeyword="keyword" /> <div class="tabs">
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router' // IMPORT useRoute and useRouter
import HeaderBar from '@/components/HeaderBar.vue'
import axios from 'axios' // Assuming you'll fetch posts

const route = useRoute() // INSTANTIATE useRoute
const router = useRouter() // INSTANTIATE useRouter

type TabType = 'recommend' | 'follow' | 'hot';
const activeTab = ref<TabType>('recommend')
const keyword = ref('') // This will hold the search term
const isLoading = ref(false);

// Define a Post interface matching your expected data structure
interface User {
  id: number;
  username: string;
  avatar?: string;
}
interface Post {
  id: number;
  userId: number;
  title: string;
  content: string;
  tags?: string[]; // Expect tags as an array of strings
  user?: User; // Include if author info is nested
  authorName?: string; // Fallback if user object is not directly available
  createdAt: string; // Or whatever your date field is
  views?: number;
  likes?: number;
}

const allPosts = ref<Post[]>([]) // Store all fetched posts

// --- Fetching Posts ---
const fetchPosts = async () => {
  isLoading.value = true;
  console.log(`Workspaceing posts for tab: ${activeTab.value}, keyword: ${keyword.value}`);
  try {
    let url = 'http://127.0.0.1:5000/article/recommend'; // Default to recommend
    const params: any = {};

    // Tab-specific endpoints (adjust as needed)
    if (activeTab.value === 'follow') {
      url = 'http://127.0.0.1:5000/article/following'; // Needs authentication
    } else if (activeTab.value === 'hot') {
      url = 'http://127.0.0.1:5000/article/hot';
    }
    // If there's a search keyword, we might use a general search endpoint
    // or let the frontend filter if the backend doesn't support search on these specific tabs.
    // For simplicity here, we'll assume frontend filtering for keywords unless it's a dedicated search.
    // If keyword is present, it might override tab or use a specific search API.
    // This example will fetch by tab, then filter by keyword on frontend.

    const token = localStorage.getItem('token');
    const headers: any = {};
    if (token && activeTab.value === 'follow') { // Only send token if needed, e.g., for 'follow' tab
        headers.Authorization = `Bearer ${token}`;
    }

    // If you have a dedicated search API endpoint:
    if (keyword.value) {
        url = `http://127.0.0.1:5000/article/search`;
        params.keyword = keyword.value;
        // If search API also needs tab context, add it to params
        // params.tab = activeTab.value;
    }


    const response = await axios.get(url, { headers, params });
    if (response.data && Array.isArray(response.data.data)) {
      allPosts.value = response.data.data.map((post: any) => ({
        ...post,
        tags: post.tag ? post.tag.split(/,|，/).map((t: string) => t.trim()).filter((t:string) => t) : []
      }));
    } else if (Array.isArray(response.data)) { // If API returns array directly
        allPosts.value = response.data.map((post: any) => ({
        ...post,
        tags: post.tag ? post.tag.split(/,|，/).map((t: string) => t.trim()).filter((t:string) => t) : []
      }));
    }
    else {
      allPosts.value = [];
      console.warn("No posts data found or in unexpected format", response.data);
    }
  } catch (error) {
    console.error('Error fetching posts:', error)
    allPosts.value = [];
  } finally {
    isLoading.value = false;
  }
}


// According to keyword filter articles
const filteredPosts = computed(() => {
  let listToFilter = [...allPosts.value];

  if (!keyword.value) {
    return listToFilter;
  }

  const searchTerm = keyword.value.toLowerCase();
  return listToFilter.filter(post =>
    (post.title && post.title.toLowerCase().includes(searchTerm)) ||
    (post.content && post.content.toLowerCase().includes(searchTerm)) ||
    (post.user?.username && post.user.username.toLowerCase().includes(searchTerm)) ||
    (post.authorName && post.authorName.toLowerCase().includes(searchTerm)) ||
    (post.tags && post.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
  );
});

// Update keyword from HeaderBar search
const handleSearch = (newKeyword: string) => {
  // When search is initiated from HeaderBar, update URL query and keyword
  router.push({ query: newKeyword ? { search: newKeyword } : {} });
  // The watchEffect below will handle setting keyword.value from route.query
};

// Watch for route query changes to update the keyword
watch(() => route.query.search, (newSearchTerm) => {
  const term = Array.isArray(newSearchTerm) ? newSearchTerm[0] : newSearchTerm;
  keyword.value = term || '';
  // No need to call fetchPosts() here if search is purely frontend
  // If your backend handles search, then you might call fetchPosts()
  if (term) { // If there's a search term, fetch with it
    fetchPosts();
  } else if (!term && allPosts.value.length === 0) { // If search cleared and no posts, fetch by tab
    fetchPosts();
  }
  // If search is cleared but posts for the tab were already loaded, no need to re-fetch,
  // the computed `filteredPosts` will just return all posts for the current tab.

}, { immediate: true }); // immediate: true to run on component mount


// Watch for activeTab changes to re-fetch posts
watch(activeTab, () => {
    // When tab changes, clear keyword unless you want persistent search across tabs
    // For this example, let's clear the search term and URL when tab changes
    if (keyword.value) {
        keyword.value = ''; // Clear local keyword
        router.push({ query: {} }); // Clear search query from URL
    }
    fetchPosts();
});


onMounted(() => {
  // Initial fetch based on current route query or default tab
  // The 'watch' on route.query.search with immediate: true handles initial keyword
  // If no search query, fetch posts for the default active tab
  if (!route.query.search) {
    fetchPosts();
  }
});

function setActiveTab(tab: TabType) {
  activeTab.value = tab;
  // Fetching is handled by the watcher on activeTab
}

function goToPost(id: number | string) {
  router.push(`/post/${id}`);
}

// Function to generate excerpt (similar to Profile.vue but can be moved to a utility file)
function getExcerpt(content: string, length: number = 100): string {
  if (!content) return '暂无内容预览...';
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = content; // Handle HTML content
  const text = tempDiv.textContent || tempDiv.innerText || '';
  return text.length > length ? text.slice(0, length) + '...' : text;
}

// For clicking tags within the Home page itself
function searchByTag(tag: string) {
  if (!tag) return;
  // This will update the route, and the watcher on route.query.search will do the rest
  router.push({ query: { search: tag } });
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