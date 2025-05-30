<template>
  <!-- 组件的 HTML 模板 -->
  <div class="user-liked-articles">
    <h2>用户点赞文章列表</h2>
    <div v-if="mergedIsLoading" class="loading">
      加载中...
    </div>
    <div v-else>
      <h3>用户 {{ userInfo.nickname }} (ID: {{ userId }}) 点赞的文章</h3>
      <table class="liked-articles-table">
        <thead>
          <tr>
            <th>文章ID</th>
            <th>文章标题</th>
            <th>点赞时间</th>
            <th>文章作者</th>
            <th>阅读量</th>
            <th>评论数</th>
            <th>点赞数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="article in likedArticles" :key="article.article_info.id">
            <td>{{ article.article_info.id }}</td>
            <td>{{ article.article_info.title }}</td>
            <td>{{ formatDate(article.like_create_time) }}</td>
            <td>{{ article.article_info.author }}</td>
            <td>{{ article.article_info.read_count }}</td>
            <td>{{ article.article_info.comments_count }}</td>
            <td>{{ article.article_info.likes_count }}</td>
          </tr>
        </tbody>
      </table>
      <button @click="backToList">返回用户列表</button>
    </div>
  </div>
</template>

<script>
// 组件的逻辑
import axios from 'axios';

export default {
  props: {
    userId: {
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
      likedArticles: [],
      localIsLoading: false,
      userInfo: {}
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  watch: {
    userId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchUserLikedArticles();
          this.fetchUserInfo();
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
    async fetchUserLikedArticles() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/user/${this.userId}/liked-articles`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.likedArticles = response.data.liked_articles;
        }
      } catch (error) {
        console.error('获取用户点赞文章失败:', error);
        alert('获取用户点赞文章失败，请稍后再试');
      } finally {
        this.localIsLoading = false;
      }
    },
    async fetchUserInfo() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/user/${this.userId}`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.userInfo = response.data.user;
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.userInfo = { nickname: '未知用户' };
      }
    },
    backToList() {
      this.$emit('back-to-list');
    }
  }
};
</script>

<style scoped>
/* 组件的样式 */
.user-liked-articles {
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

.liked-articles-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 14px;
  color: #333;
  margin-bottom: 20px;
}

.liked-articles-table th,
.liked-articles-table td {
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.liked-articles-table th {
  background-color: #f2f2f2;
  font-weight: 600;
  color: #555;
}

.liked-articles-table tbody tr:nth-child(even) {
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