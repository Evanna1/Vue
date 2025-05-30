<template>
  <div class="comment-like-users-container">
    <h2>评论点赞用户列表</h2>
    <div v-if="mergedIsLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>
    <div v-else>
      <h3>评论内容：{{ commentContent }}</h3>
      <p>点赞数：{{ likeCount }}</p>
      <table class="like-users-table">
        <thead>
          <tr>
            <th>用户ID</th>
            <th>用户名</th>
            <th>昵称</th>
            <th>头像</th>
            <th>点赞时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in likeUsers" :key="user.user_info.id">
            <td>{{ user.user_info.id }}</td>
            <td>{{ user.user_info.username }}</td>
            <td>{{ user.user_info.nickname }}</td>
            <td>
              <img :src="user.user_info.avatar" :alt="user.user_info.nickname" class="avatar">
            </td>
            <td>{{ formatDate(user.like_create_time) }}</td>
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
    commentId: {
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
      commentContent: '',
      likeCount: 0,
      likeUsers: [],
      localIsLoading: false
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  created() {
    this.loadCommentLikeUsers();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async loadCommentLikeUsers() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/comment/${this.commentId}/like-users`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        const data = response.data;
        if (data.state === 1) {
          this.commentContent = data.comment_content;
          this.likeCount = data.like_count;
          this.likeUsers = data.like_users;
        } else {
          console.error('获取评论点赞用户失败:', data.message);
        }
      } catch (error) {
        console.error('请求评论点赞用户接口失败:', error);
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
.comment-like-users-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #5ea8da;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

h3 {
  margin-top: 20px;
  margin-bottom: 15px;
}

.like-users-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 14px;
  color: #333;
  margin-bottom: 20px;
}

.like-users-table th,
.like-users-table td {
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.like-users-table th {
  background-color: #f2f2f2;
  font-weight: 600;
  color: #555;
}

.like-users-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.like-users-table tbody tr:hover {
  background-color: #f0f0f0;
  transition: background-color 0.3s ease;
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  object-fit: cover;
}

button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #4a90c2;
}
</style>