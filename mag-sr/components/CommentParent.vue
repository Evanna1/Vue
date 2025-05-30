<template>
  <div class="comment-parent-container">
    <h2>父评论</h2>
    <div v-if="mergedIsLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>
    <div v-else>
      <h3>父评论ID：{{ parentComment.parent_comment_id }}</h3>
      <p><strong>内容：</strong>{{ parentComment.content }}</p>
      <p><strong>创建时间：</strong>{{ formatDate(parentComment.create_time) }}</p>
      <p><strong>更新时间：</strong>{{ formatDate(parentComment.update_time) }}</p>
      <p><strong>状态：</strong>{{ formatStatus(parentComment.status) }}</p>
      <p><strong>点赞数：</strong>{{ parentComment.like_count }}</p>
      <p><strong>回复数：</strong>{{ parentComment.reply_count }}</p>
      <p><strong>深度：</strong>{{ parentComment.depth }}</p>
      <div class="user-info">
        <img :src="parentComment.user.avatar" :alt="parentComment.user.nickname" class="avatar">
        <span>{{ parentComment.user.nickname }}</span>
      </div>
      <button @click="backToList">返回列表</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    parentId: {
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
      parentComment: {},
      localIsLoading: false
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  created() {
    this.loadCommentParent();
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
    async loadCommentParent() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/comment/${this.parentId}/parent`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        const data = response.data;
        if (data.state === 1) {
          this.parentComment = data.parent_comment;
        } else {
          console.error('获取父评论失败:', data.message);
          alert(data.message);
        }
      } catch (error) {
        console.error('请求父评论接口失败:', error);
        alert('获取父评论失败，请稍后再试');
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
.comment-parent-container {
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

.user-info {
  display: flex;
  align-items: center;
  margin: 15px 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 10px;
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
  margin-top: 15px;
}

button:hover {
  background-color: #4a90c2;
}
</style>