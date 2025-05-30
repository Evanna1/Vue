<template>
  <div class="article-favorites">
    <h2>文章收藏列表</h2>
    <div v-if="mergedIsLoading" class="loading">
      加载中...
    </div>
    <div v-else>
      <h3>收藏了文章 {{ articleId }} 的用户</h3>
      <table class="favorites-table">
        <thead>
          <tr>
            <th>用户ID</th>
            <th>用户名</th>
            <th>收藏时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in favorites" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ formatDate(user.create_at) }}</td>
          </tr>
        </tbody>
      </table>
      <button @click="backToList">返回列表</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    articleId: {
      type: [String, Number],
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      favorites: [],
      localIsLoading: false
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  watch: {
    articleId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchArticleFavorites();
        }
      }
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async fetchArticleFavorites() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/favorites/${this.articleId}`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.favorites = response.data.favorites;
        }
      } catch (error) {
        console.error('获取文章收藏列表失败:', error);
        alert('获取文章收藏列表失败，请稍后再试');
      } finally {
        this.localIsLoading = false;
      }
    },
    backToList() {
      this.$emit('back-to-list');
    }
  }
};
</script>

<style scoped>
.article-favorites {
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  text-align: left;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 16px;
  color: #666;
}

.favorites-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 14px;
  color: #333;
  margin-bottom: 20px;
}

.favorites-table th,
.favorites-table td {
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.favorites-table th {
  background-color: #f2f2f2;
  font-weight: 600;
  color: #555;
}

.favorites-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
  margin-top: 20px;
}

button:hover {
  background-color: #4a90c2;
}
</style>