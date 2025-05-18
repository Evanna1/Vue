<template>
  <div class="article-table-container">
    <div class="table-responsive"> <table class="article-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>标题</th>
          <th>作者</th>
          <th>创建时间</th>
          <th>更新时间</th>
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
        <tr v-for="article in articles" :key="article.id">
          <td>{{ article.id }}</td>
          <td>{{ article.title }}</td>
          <td>{{ article.author }}</td>
          <td>{{ formatDate(article.create_time) }}</td>
          <td>{{ formatDate(article.update_time) }}</td>
          <td>{{ formatStatus(article.status) }}</td>
          <td>{{ formatPermission(article.permission) }}</td>
          <td>{{ article.read_count }}</td>
          <td>{{ article.comments_count }}</td>
          <td>{{ article.likes_count }}</td>
          <td>{{ article.favorites_count }}</td>
          <td>
            <button class="button" @click="viewArticleDetail(article.id)">详情</button>
            <button class="button" @click="openPermissionModal(article)">修改权限</button>
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
</template>

<script>
import axios from 'axios';

export default {
  props: {
    articles: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      isPermissionModalOpen: false,
      permissionForm: {
        article_id: '',
        new_permission: '0'
      },
      currentArticle: null
    };
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
        this.$emit('refresh-articles');
        this.closePermissionModal();
        alert('文章权限更新成功');
      } catch (error) {
        console.error('更新文章权限失败:', error);
        alert('更新权限失败，请稍后再试');
      }
    },
    viewArticleDetail(articleId) {
      this.$router.push(`/article-detail/${articleId}`);
    }
  }
}
</script>

<style scoped>
.article-table-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  /* 可以设置一个合理的 max-width，如果希望卡片不要无限延伸 */
  /* max-width: 1200px; */
}

/* 控制表格的水平滚动 */
.table-responsive {
  overflow-x: auto;
}

.article-table {
  width: 100%; /* 默认宽度为父容器的 100% */
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 14px;
  color: #333;
  white-space: nowrap; /* 确保内容不换行 */
}

.article-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.04);
}

.article-table th,
.article-table td {
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.article-table th {
  font-weight: 600;
  color: #555;
}

.article-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.article-table tbody tr:hover {
  background-color: #f0f0f0;
  transition: background-color 0.3s ease;
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

/* 模态框样式 */
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
</style>