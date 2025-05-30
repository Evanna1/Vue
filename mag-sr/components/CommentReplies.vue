<template>
  <div class="comment-replies-container">
    <h2>评论回复列表</h2>
    <div v-if="mergedIsLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>
    <div v-else>
      <h3>评论内容：{{ commentContent }}</h3>
      <p>回复数：{{ replyCount }}</p>
      <table class="replies-table">
        <thead>
          <tr>
            <th>回复ID</th>
            <th>内容</th>
            <th>创建时间</th>
            <th>更新时间</th>
            <th>状态</th>
            <th>点赞数</th>
            <th>回复数</th>
            <th>深度</th>
            <th>用户</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="reply in replies" :key="reply.reply_id">
            <td>{{ reply.reply_id }}</td>
            <td>{{ reply.content }}</td>
            <td>{{ formatDate(reply.create_time) }}</td>
            <td>{{ formatDate(reply.update_time) }}</td>
            <td>{{ formatStatus(reply.status) }}</td>
            <td>{{ reply.like_count }}</td>
            <td>{{ reply.reply_count }}</td>
            <td>{{ reply.depth }}</td>
            <td>
              <img :src="reply.user.avatar" :alt="reply.user.nickname" class="avatar">
              {{ reply.user.nickname }}
            </td>
            <td>
              <button @click="approveReply(reply.reply_id)">审核</button>
              <button @click="deleteReply(reply.reply_id)">删除</button>
            </td>
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
      replyCount: 0,
      replies: [],
      localIsLoading: false
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  created() {
    this.loadCommentReplies();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    formatStatus(status) {
      const statusMap = {
        0: '正常',
        1: '已删除',
        2: '屏蔽',
        3: '举报'
      };
      return statusMap[status] || '未知状态';
    },
    async loadCommentReplies() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/comment/${this.commentId}/replies`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        const data = response.data;
        if (data.state === 1) {
          this.commentContent = data.comment_content;
          this.replyCount = data.reply_count;
          this.replies = data.replies;
        } else {
          console.error('获取评论回复失败:', data.message);
        }
      } catch (error) {
        console.error('请求评论回复接口失败:', error);
      } finally {
        this.localIsLoading = false;
      }
    },
    async approveReply(replyId) {
      try {
        const token = localStorage.getItem('token');
        await axios.post(
          `http://localhost:5000/manager/comment/${replyId}/review`,
          { approved: true },
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        alert('审核成功');
        this.loadCommentReplies();
      } catch (error) {
        console.error('审核回复失败:', error);
        alert('审核失败，请稍后再试');
      }
    },
    async deleteReply(replyId) {
      try {
        const token = localStorage.getItem('token');
        await axios.post(
          `http://localhost:5000/manager/comment/${replyId}/delete`,
          {},
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        alert('删除成功');
        this.loadCommentReplies();
      } catch (error) {
        console.error('删除回复失败:', error);
        alert('删除失败，请稍后再试');
      }
    },
    backToList() {
      this.$emit('back-to-list');
    }
  }
};
</script>

<style scoped>
.comment-replies-container {
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

.replies-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 14px;
  color: #333;
  margin-bottom: 20px;
}

.replies-table th,
.replies-table td {
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.replies-table th {
  background-color: #f2f2f2;
  font-weight: 600;
  color: #555;
}

.replies-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.replies-table tbody tr:hover {
  background-color: #f0f0f0;
  transition: background-color 0.3s ease;
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 10px;
}

button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
  margin-right: 5px;
}

button:hover {
  background-color: #4a90c2;
}
</style>