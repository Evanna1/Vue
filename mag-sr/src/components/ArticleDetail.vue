<template>
  <div class="article-detail-container">
    <div v-if="article" class="article-detail">
      <h1>{{ article.title }}</h1>
      <div class="article-meta">
        <span>作者: {{ article.author }}</span>
        <span>创建时间: {{ formatDate(article.create_time) }}</span>
      </div>
      <div class="article-content">
        <div v-if="article.image_path" class="article-image">
          <img :src="article.image_path" alt="文章图片">
        </div>
        <div class="article-text" v-html="article.content"></div>
      </div>
      <div class="article-stats">
        <div class="stat-item">
          <span>阅读量: {{ article.read_count }}</span>
        </div>
        <div class="stat-item">
          <span>评论数: {{ article.comments_count }}</span>
        </div>
        <div class="stat-item">
          <span>点赞数: {{ article.likes_count }}</span>
        </div>
        <div class="stat-item">
          <span>收藏数: {{ article.favorites_count }}</span>
        </div>
        <div class="stat-item">
          <span>状态: {{ formatStatus(article.status) }}</span>
        </div>
        <div class="stat-item">
          <span>权限: {{ formatPermission(article.permission) }}</span>
        </div>
      </div>
    </div>
    <div v-else>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      article: null
    };
  },
  created() {
    this.fetchArticleDetail();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    formatStatus(status) {
      const statusMap = {
        0: '已发布',
        1: '已删除',
        2: '被举报'
      };
      return statusMap[status] || '未知状态';
    },
    formatPermission(permission) {
      return permission === '0' ? '公开' : '屏蔽';
    },
    fetchArticleDetail() {
      const articleId = this.$route.params.articleId;
      try {
        const token = localStorage.getItem('token');
        axios.get(`http://localhost:5000/manager/article_detail/${articleId}`, {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        }).then(response => {
          if (response.data.state === 1) {
            this.article = response.data.article;
          } else {
            console.error('获取文章详情失败:', response.data.message);
          }
        }).catch(error => {
          console.error('请求文章详情接口失败:', error);
        });
      } catch (error) {
        console.error('获取文章详情失败:', error);
      }
    }
  }
}
</script>

<style scoped>
.article-detail-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.article-detail h1 {
  font-size: 24px;
  margin-bottom: 10px;
}

.article-meta {
  display: flex;
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.article-meta span {
  margin-right: 15px;
}

.article-content {
  margin-bottom: 20px;
}

.article-image img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.article-text {
  line-height: 1.6;
}

.article-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.stat-item {
  flex: 1;
  min-width: 120px;
  padding: 8px 12px;
  background-color: #f5f5f5;
  border-radius: 6px;
}

.stat-item span {
  font-size: 14px;
}
</style>