<template>
  <div class="user-table-container">
    <div class="search-container">
      <input type="text" v-model="searchKeyword" @input="filterUsers" placeholder="输入关键词搜索用户...">
      <select v-model="searchField" style="margin-left: 10px; padding: 5px; border-radius: 4px; border: 1px solid #ddd;">
        <option value="">不限</option>
        <option value="id">ID</option>
        <option value="username">用户名</option>
        <option value="nickname">昵称</option>
        <option value="gender">性别</option>
        <option value="email">邮箱</option>
        <option value="phone">手机号</option>
        <option value="create_at">注册时间</option>
      </select>
    </div>
    <div class="table-responsive">
      <table class="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>昵称</th>
            <th>头像</th>
            <th>性别</th>
            <th>邮箱</th>
            <th>手机号</th>
            <th>注册时间</th>
            <th>最后登录时间</th>
            <th>是否在线</th>
            <th>状态</th>
            <th>发布权限</th>
            <th>评论权限</th>
            <th>文章数</th>
            <th>评论数</th>
            <th>点赞数</th>
            <th>粉丝数</th>
            <th>关注数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.nickname }}</td>
            <td>
              <img :src="user.avatar" alt="头像" style="width: 30px; height: 30px; border-radius: 50%;">
            </td>
            <td>{{ user.gender }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.phone }}</td>
            <td>{{ formatDate(user.create_at) }}</td>
            <td>{{ formatDate(user.last_login_at) }}</td>
            <td>{{ user.is_online ? '是' : '否' }}</td>
            <td>{{ user.u_status === 0 ? '正常' : '封禁' }}</td>
            <td>{{ user.is_publish === 1 ? '有' : '无' }}</td>
            <td>{{ user.is_comment === 1 ? '有' : '无' }}</td>
            <td>{{ user.article_count }}</td>
            <td>{{ user.comment_count }}</td>
            <td>{{ user.like_count }}</td>
            <td>{{ user.followers_count }}</td>
            <td>{{ user.followings_count }}</td>
            <td>
              <button class="button" @click="goToUserProfile(user.id)">主页</button>
              <button class="button" @click="openStatusModal(user)">修改状态</button>
              <button class="button" @click="openPermissionModal(user)">修改权限</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isStatusModalOpen" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeStatusModal">&times;</span>
        <h2>修改用户状态</h2>
        <form @submit.prevent="submitStatusChange">
          <div class="form-group">
            <label for="username">用户名</label>
            <input type="text" id="username" v-model="statusForm.username" readonly>
          </div>
          <div class="form-group">
            <label for="new_status">新状态</label>
            <select id="new_status" v-model="statusForm.new_status">
              <option value="0">正常</option>
              <option value="1">封禁</option>
            </select>
          </div>
          <button type="submit" class="submit-button">提交</button>
          <button type="button" @click="closeStatusModal" class="cancel-button">取消</button>
        </form>
      </div>
    </div>

    <div v-if="isPermissionModalOpen" class="modal">
      <div class="modal-content">
        <span class="close" @click="closePermissionModal">&times;</span>
        <h2>修改用户权限</h2>
        <form @submit.prevent="submitPermissionChange">
          <div class="form-group">
            <label for="username_perm">用户名</label>
            <input type="text" id="username_perm" v-model="permissionForm.username" readonly>
          </div>
          <div class="form-group">
            <label for="is_publish">发布权限</label>
            <select id="is_publish" v-model="permissionForm.is_publish">
              <option value="1">有</option>
              <option value="0">无</option>
            </select>
          </div>
          <div class="form-group">
            <label for="is_comment">评论权限</label>
            <select id="is_comment" v-model="permissionForm.is_comment">
              <option value="1">有</option>
              <option value="0">无</option>
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
    users: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      searchKeyword: '',
      searchField: '',
      filteredUsers: this.users,
      isStatusModalOpen: false,
      isPermissionModalOpen: false,
      statusForm: {
        username: '',
        new_status: '0'
      },
      permissionForm: {
        username: '',
        is_publish: '1',
        is_comment: '1'
      },
      currentStatusUser: null,
      currentPermissionUser: null
    };
  },
  watch: {
    users: {
      handler(newVal) {
        this.filteredUsers = newVal;
      },
      immediate: true
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    filterUsers() {
      if (!this.searchKeyword) {
        this.filteredUsers = this.users;
        return;
      }
      this.filteredUsers = this.users.filter(user => {
        if (!this.searchField) {
          return (
            user.id.toString().includes(this.searchKeyword) ||
            user.username.includes(this.searchKeyword) ||
            user.nickname.includes(this.searchKeyword) ||
            user.gender.includes(this.searchKeyword) ||
            user.email.includes(this.searchKeyword) ||
            user.phone.includes(this.searchKeyword) ||
            (user.create_at && user.create_at.includes(this.searchKeyword)) ||
            (user.last_login_at && user.last_login_at.includes(this.searchKeyword))
          );
        } else {
          const value = user[this.searchField];
          return value && value.toString().includes(this.searchKeyword);
        }
      });
    },
    openStatusModal(user) {
      this.statusForm.username = user.username;
      this.statusForm.new_status = user.u_status;
      this.currentStatusUser = user;
      this.isStatusModalOpen = true;
    },
    closeStatusModal() {
      this.isStatusModalOpen = false;
    },
    openPermissionModal(user) {
      this.permissionForm.username = user.username;
      this.permissionForm.is_publish = user.is_publish;
      this.permissionForm.is_comment = user.is_comment;
      this.currentPermissionUser = user;
      this.isPermissionModalOpen = true;
    },
    closePermissionModal() {
      this.isPermissionModalOpen = false;
    },
    async submitStatusChange() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          'http://localhost:5000/manager/update_user_status',
          {
            u_account: this.statusForm.username,
            new_status: parseInt(this.statusForm.new_status)
          },
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );

        if (response.data.state === 1) {
          // 更新成功后刷新用户列表并关闭模态框
          this.$emit('refresh-users');
          this.closeStatusModal();
          alert('状态更新成功');
        } else {
          alert(`状态更新失败: ${response.data.message}`);
        }
      } catch (error) {
        if (error.response && error.response.status === 400) {
          alert(`状态更新失败: ${error.response.data.message}`);
        } else {
          console.error('更新用户状态失败:', error);
          alert('更新状态失败，请稍后再试');
        }
      }
    },
    async submitPermissionChange() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          'http://localhost:5000/manager/update_user_permission',
          {
            u_account: this.permissionForm.username,
            is_publish: parseInt(this.permissionForm.is_publish),
            is_comment: parseInt(this.permissionForm.is_comment)
          },
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );

        if (response.data.state === 1) {
          // 更新成功后刷新用户列表并关闭模态框
          this.$emit('refresh-users');
          this.closePermissionModal();
          alert('权限更新成功');
        } else {
          alert(`权限更新失败: ${response.data.message}`);
        }
      } catch (error) {
        if (error.response) {
          if (error.response.status === 400 || error.response.status === 403) {
            alert(`权限更新失败: ${error.response.data.message}`);
          } else {
            alert(`服务器返回错误: ${error.response.status}`);
          }
        } else {
          console.error('更新用户权限失败:', error);
          alert('更新权限失败，请稍后再试');
        }
      }
    },
    goToUserProfile(userId) {  // 添加跳转到用户主页的方法
      this.$router.push(`/user/${userId}`);  // 跳转到用户主页路由
    }
  }
}
</script>

<style scoped>
.user-table-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.search-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

.search-container input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  width: 250px;
}

.table-responsive {
  overflow-x: auto;
}

.user-table {
  width: auto;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.user-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.04);
}

.user-table th,
.user-table td {
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.user-table th {
  font-weight: 600;
  color: #555;
}

.user-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.user-table tbody tr:hover {
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