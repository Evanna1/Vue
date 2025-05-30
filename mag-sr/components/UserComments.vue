<template>
  <div class="user-comments">
    <h2>用户评论列表</h2>
    <div v-if="mergedIsLoading" class="loading">
      加载中...
    </div>
    <div v-else>
      <h3>用户 {{ userInfo.nickname }} (ID: {{ userId }}) 的评论记录</h3>
      <table class="comments-table">
        <thead>
          <tr>
            <th>评论ID</th>
            <th>文章ID</th>
            <th>文章标题</th>
            <th>评论内容</th>
            <th>评论时间</th>
            <th>更新时间</th>
            <th>状态</th>
            <th>点赞数</th>
            <th>回复数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="comment in comments" :key="comment.comment_id">
            <td>{{ comment.comment_id }}</td>
            <td>{{ comment.article_id }}</td>
            <td>{{ comment.article_title }}</td>
            <td>{{ comment.comment_content }}</td>
            <td>{{ formatDate(comment.comment_create_time) }}</td>
            <td>{{ formatDate(comment.comment_update_time) }}</td>
            <td>
              <span :class="['comment-status', comment.comment_status === 0 ? 'normal' : 'blocked']">
                {{ comment.comment_status === 0 ? '正常' : '已删除' }}
              </span>
            </td>
            <td>{{ comment.comment_like_count }}</td>
            <td>{{ comment.comment_reply_count }}</td>
          </tr>
        </tbody>
      </table>
      <button @click="backToList">返回用户列表</button>
    </div>
  </div>
</template>

<script>
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
      comments: [],
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
          this.fetchUserComments();
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
    async fetchUserComments() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/user/${this.userId}/comments`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.comments = response.data.comments;
        }
      } catch (error) {
        console.error('获取用户评论记录失败:', error);
        alert('获取用户评论记录失败，请稍后再试');
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
.user-comments {
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

.comments-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 14px;
  color: #333;
  margin-bottom: 20px;
}

.comments-table th,
.comments-table td {
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.comments-table th {
  background-color: #f2f2f2;
  font-weight: 600;
  color: #555;
}

.comments-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.comment-status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.normal {
  background-color: #dff0d8;
  color: #3c763d;
}

.blocked {
  background-color: #fdecea;
  color: #d9534f;
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