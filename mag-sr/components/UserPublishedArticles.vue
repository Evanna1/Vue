<template>
  <div class="user-published-articles">
    <button @click="backToList" class="back-button">返回</button>
    <div class="header-container">
      <h3 class="page-title">用户 {{ userInfo }}(ID: {{ userId }}) 发布过的文章</h3>
    </div>
    <div class="search-filter-container">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
        <input type="text" v-model="searchKeyword" @input="filterArticles" placeholder="输入关键词搜索文章...">
      </div>
      <div class="filter-select">
        <select v-model="searchField">
          <option value="">不限</option>
          <option value="id">ID</option>
          <option value="title">标题</option>
          <option value="status">状态</option>
          <option value="permission">权限</option>
          <option value="create_time">创建时间</option>
          <option value="update_time">更新时间</option>
        </select>
      </div>
    </div>
    <div v-if="mergedIsLoading" class="loading">
      加载中...
    </div>
    <div v-else class="articles-content">
      <div class="table-wrapper">
        <table class="articles-table">
          <thead>
            <tr>
              <th>文章ID</th>
              <th>标题</th>
              <th>创建时间</th>
              <th>更新时间</th>
              <th>标签</th>
              <th>状态</th>
              <th>权限</th>
              <th>阅读量</th>
              <th>评论数</th>
              <th>点赞数</th>
              <th>收藏数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="article in filteredArticles" :key="article.id">
              <td>
                <a @click="showArticleDetail(article.id)">{{ article.id }}</a>
              </td>
              <td>{{ article.title }}</td>
              <td>{{ formatDate(article.create_time) }}</td>
              <td>{{ formatDate(article.update_time) }}</td>
              <td>{{ article.tag }}</td>
              <td>{{ formatStatus(article.status) }}</td>
              <td>{{ article.permission === 0 ? '公开' : '屏蔽' }}</td>
              <td>
                <a @click="showArticleBrowsers(article.id)">{{ article.read_count }}</a>
              </td>
              <td>
                <a @click="showArticleCommentUsers(article.id)">{{ article.comments_count }}</a>
              </td>
              <td>
                <a @click="showArticleLikeUsers(article.id)">{{ article.likes_count }}</a>
              </td>
              <td>
                <a @click="showArticleFavorites(article.id)">{{ article.favorites_count }}</a>
              </td>
              <td>
                <button @click="showArticleDetail(article.id)">详情</button>
                <button @click="openPermissionModal(article)">修改权限</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="isPermissionModalOpen" class="modal">
        <div class="modal-content">
          <span class="close" @click="closePermissionModal">&times;</span>
          <h2>修改文章权限</h2>
          <form @submit.prevent="submitPermissionChange">
            <div class="form-group">
              <label for="article_id_perm">文章ID</label>
              <input type="text" id="article_id_perm" v-model="permissionForm.article_id" readonly>
            </div>
            <div class="form-group">
              <label for="new_permission">新权限</label>
              <select id="new_permission" v-model="permissionForm.new_permission">
                <option value="0">公开</option>
                <option value="1">屏蔽</option>
              </select>
            </div>
            <button type="submit" class="submit-button">提交</button>
            <button type="button" @click="closePermissionModal" class="cancel-button">取消</button>
          </form>
        </div>
      </div>
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
    },
    initialArticles: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      publishedArticles: this.initialArticles,
      localIsLoading: false,
      userInfo: { nickname: '未知用户' },
      isPermissionModalOpen: false,
      permissionForm: {
        article_id: '',
        new_permission: '0'
      },
      currentArticle: null,
      searchKeyword: '',
      searchField: '',
      filteredArticles: [...this.initialArticles]
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
          this.fetchUserPublishedArticles();
          this.fetchUserInfo();
        }
      }
    },
    initialArticles(newVal) {
      this.publishedArticles = newVal;
      this.filteredArticles = [...newVal];
    }
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
    async fetchUserPublishedArticles() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/user/${this.userId}/published-articles`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.publishedArticles = response.data.articles;
          this.filteredArticles = [...this.publishedArticles];
        }
      } catch (error) {
        console.error('获取用户发布文章失败:', error);
        alert('获取用户发布文章失败，请稍后再试');
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
    },
    openPermissionModal(article) {
      this.permissionForm.article_id = article.id;
      this.permissionForm.new_permission = article.permission;
      this.currentArticle = article;
      this.isPermissionModalOpen = true;
    },
    closePermissionModal() {
      this.isPermissionModalOpen = false;
    },
    async submitPermissionChange() {
      try {
        const token = localStorage.getItem('token');
        await axios.patch(
          `http://localhost:5000/article/manager/update/${this.permissionForm.article_id}/permission`,
          {
            permission: parseInt(this.permissionForm.new_permission)
          },
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        this.currentArticle.permission = parseInt(this.permissionForm.new_permission);
        this.filterArticles();
        this.closePermissionModal();
        alert('文章权限更新成功');
      } catch (error) {
        console.error('更新文章权限失败:', error);
        alert('更新权限失败，请稍后再试');
      }
    },
    showArticleDetail(articleId) {
      this.$emit('show-article-detail', articleId);
    },
    showArticleFavorites(articleId) {
      this.$emit('show-article-favorites', articleId);
    },
    showArticleCommentUsers(articleId) {
      this.$emit('show-article-comment-users', articleId);
    },
    showArticleLikeUsers(articleId) {
      this.$emit('show-article-like-users', articleId);
    },
    showArticleBrowsers(articleId) {
      this.$emit('show-article-browsers', articleId);
    },
    filterArticles() {
      if (!this.searchKeyword) {
        this.filteredArticles = [...this.publishedArticles];
        return;
      }

      const keyword = this.searchKeyword.toLowerCase();
      this.filteredArticles = this.publishedArticles.filter(article => {
        let value = '';
        switch (this.searchField) {
          case 'id':
            value = article.id.toString();
            break;
          case 'title':
            value = article.title;
            break;
          case 'status':
            value = this.formatStatus(article.status);
            break;
          case 'permission':
            value = article.permission === 0 ? '公开' : '屏蔽';
            break;
          case 'create_time':
            value = this.formatDate(article.create_time);
            break;
          case 'update_time':
            value = this.formatDate(article.update_time);
            break;
          default:
            value = article.id.toString() + article.title + this.formatStatus(article.status) + (article.permission === 0 ? '公开' : '屏蔽') + this.formatDate(article.create_time) + this.formatDate(article.update_time);
        }
        return value.toLowerCase().includes(keyword);
      });
    }
  }
};
</script>

<style scoped>
.user-published-articles {
  padding: 24px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  text-align: left;
  position: relative;
}

.header-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
  margin-top: 10px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.search-filter-container {
  display: flex;
  gap: 2px;
  align-items: center;
  position: absolute;
  top: 140px;
  right: 24px;
}

.search-box {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 6px 12px;
  background-color: #fff;
}

.search-icon {
  width: 18px;
  height: 18px;
  margin-right: 8px;
  color: #888;
}

.search-box input {
  border: none;
  outline: none;
  font-size: 14px;
  color: #333;
  flex-grow: 1;
}

.filter-select {
  display: flex;
  align-items: center;
  margin-left: 10px;
}
.filter-select select {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
}

.articles-content {
  padding-top: 20px;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 30px;
}

.articles-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.articles-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.articles-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.articles-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.articles-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.articles-table tbody tr:hover {
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
}

.articles-table td a {
  color: #5ea8da;
  text-decoration: none;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 16px;
  color: #666;
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
  margin-right: 5px;
}

button:hover {
  background-color: #4a90c2;
}

.modal {
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: #fefefe;
  padding: 20px;
  border: 1px solid #888;
  width: 400px;
  max-width: 90%;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
}

.close:hover {
  color: black;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.submit-button,
.cancel-button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.submit-button {
  background-color: #5ea8da;
  color: white;
  margin-right: 10px;
}

.cancel-button {
  background-color: #f44336;
  color: white;
}

.search-filter-container {
  display: flex;
  gap: 16px;
  align-items: center;
  position: absolute;
  top: 140px;
  right: 24px;
}

.search-box {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 6px 12px;
  background-color: #fff;
}

.search-icon {
  width: 18px;
  height: 18px;
  margin-right: 8px;
  color: #888;
}

.search-box input {
  border: none;
  outline: none;
  font-size: 14px;
  color: #333;
  flex-grow: 1;
}

.filter-select {
  display: flex;
  align-items: center;
  margin-left: 10px;
}
.filter-select select {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
}
</style>