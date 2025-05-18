<template>
  <div id="managerSection">
    <div id="headerContainer" style="display: flex; justify-content: space-between; width: 100%;">
      <div id="addManagerBtnContainer">
        <button class="button" @click="openAddModal">添加管理员</button>
      </div>
      <div id="searchContainer" style="display: flex; align-items: center;">
        <input type="text" v-model="searchKeyword" @input="filterManagers" placeholder="输入关键词搜索管理员...">
        <select v-model="searchField" style="margin-left: 10px; padding: 5px; border-radius: 4px; border: 1px solid #ddd;">
          <option value="">不限</option>
          <option value="mng_id">ID</option>
          <option value="mng_name">用户名</option>
          <option value="mng_nickname">昵称</option>
          <option value="mng_gender">性别</option>
          <option value="mng_email">邮箱</option>
          <option value="mng_phone">手机号</option>
          <option value="mng_create_at">注册时间</option>
        </select>
      </div>
    </div>
    <table class="manager-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>用户名</th>
          <th>昵称</th>
          <th>性别</th>
          <th>邮箱</th>
          <th>手机号</th>
          <th>注册时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="manager in filteredManagers" :key="manager.mng_id">
          <td>{{ manager.mng_id }}</td>
          <td>{{ manager.mng_name }}</td>
          <td>{{ manager.mng_nickname }}</td>
          <td>{{ manager.mng_gender }}</td>
          <td>{{ manager.mng_email }}</td>
          <td>{{ manager.mng_phone }}</td>
          <td>{{ manager.mng_create_at }}</td>
          <td>
            <button class="button delete-button" @click="confirmDelete(manager.mng_id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 添加管理员模态框 -->
    <div v-if="isAddModalOpen" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeAddModal">&times;</span>
        <h2>添加新管理员</h2>
        <form @submit.prevent="submitAddManager">
          <div class="form-group">
            <label for="m_name">用户名</label>
            <input type="text" id="m_name" v-model="addForm.m_name" required>
          </div>
          <div class="form-group">
            <label for="m_password">密码</label>
            <input type="password" id="m_password" v-model="addForm.m_password" required>
          </div>
          <div class="form-group">
            <label for="confirm_password">确认密码</label>
            <input type="password" id="confirm_password" v-model="addForm.confirm_password" required>
          </div>
          <div class="form-group">
            <label for="m_gender">性别</label>
            <select id="m_gender" v-model="addForm.m_gender" required>
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </div>
          <div class="form-group">
            <label for="m_nickname">昵称</label>
            <input type="text" id="m_nickname" v-model="addForm.m_nickname" required>
          </div>
          <div class="form-group">
            <label for="m_phone">电话</label>
            <input type="tel" id="m_phone" v-model="addForm.m_phone" required>
          </div>
          <div class="form-group">
            <label for="m_email">邮箱</label>
            <input type="email" id="m_email" v-model="addForm.m_email" required>
          </div>
          <button type="submit" class="submit-button">添加</button>
          <button type="button" @click="closeAddModal" class="cancel-button">取消</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['managers'],
  data() {
    return {
      isAddModalOpen: false,
      addForm: {
        m_name: '',
        m_password: '',
        confirm_password: '',
        m_gender: '',
        m_nickname: '',
        m_phone: '',
        m_email: ''
      },
      managerToDelete: null,
      searchKeyword: '',
      searchField: '', // 搜索栏旁边的下拉选择框，用于选择搜索字段
      filteredManagers: []
    }
  },
  watch: {
    managers: {
      handler(newVal) {
        this.filteredManagers = newVal;
      },
      immediate: true
    }
  },
  methods: {
    openAddModal() {
      this.isAddModalOpen = true;
    },
    closeAddModal() {
      this.isAddModalOpen = false;
      this.addForm = {
        m_name: '',
        m_password: '',
        confirm_password: '',
        m_gender: '',
        m_nickname: '',
        m_phone: '',
        m_email: ''
      };
    },
    async submitAddManager() {
      if (!this.addForm.m_password || !this.addForm.confirm_password) {
        alert('请输入密码和确认密码');
        return;
      }
      if (this.addForm.m_password !== this.addForm.confirm_password) {
        alert('两次输入的密码不一致');
        return;
      }

      if (!this.addForm.m_name || !this.addForm.m_gender || !this.addForm.m_nickname || !this.addForm.m_phone || !this.addForm.m_email) {
        alert('请填写所有必填字段');
        return;
      }

      try {
        const token = localStorage.getItem('token');
        const response = await axios.post('http://localhost:5000/manager/add_mng', {
          m_name: this.addForm.m_name,
          m_password: this.addForm.m_password,
          m_gender: this.addForm.m_gender,
          m_nickname: this.addForm.m_nickname,
          m_avatar: this.addForm.m_avatar,
          m_phone: this.addForm.m_phone,
          m_email: this.addForm.m_email
        }, {
          headers: {
            'Authorization': 'Bearer ' + token,
          }
        });

        const data = response.data;
        if (data.state === 1) {
          alert(data.message);
          this.closeAddModal();
          this.$emit('refresh-managers');
        } else {
          alert(`添加失败: ${data.message}`);
        }
      } catch (error) {
        console.error('Error adding manager:', error);
        if (error.response && error.response.data && error.response.data.message) {
          alert(`添加管理员失败: ${error.response.data.message}`);
        } else {
          alert('添加失败，请稍后再试');
        }
      }
    },
    confirmDelete(managerId) {
      if (confirm(`确定要删除管理员 ${this.managers.find(m => m.mng_id === managerId).mng_name} 吗？`)) {
        this.deleteManager(managerId);
      }
    },
    async deleteManager(managerId) {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.delete('http://localhost:5000/manager/delete_mng', {
          headers: {
            'Authorization': 'Bearer ' + token,
          },
          data: {
            delete_by: 'mng_id',
            value: managerId
          }
        });

        const data = response.data;
        if (data.state === 1) {
          alert(data.message);
          this.$emit('refresh-managers');
        } else {
          alert(`删除失败: ${data.message}`);
        }
      } catch (error) {
        console.error('Error deleting manager:', error);
        alert(error.response?.data?.message || '删除失败，请稍后再试');
      }
    },
    filterManagers() {
      if (!this.searchKeyword) {
        this.filteredManagers = this.managers;
        return;
      }
      this.filteredManagers = this.managers.filter(manager => {
        if (!this.searchField) { // 不限条件搜索
          return (
            manager.mng_id.toString().includes(this.searchKeyword) ||
            manager.mng_name.includes(this.searchKeyword) ||
            manager.mng_nickname.includes(this.searchKeyword) ||
            manager.mng_gender.includes(this.searchKeyword) ||
            manager.mng_email.includes(this.searchKeyword) ||
            manager.mng_phone.includes(this.searchKeyword) ||
            manager.mng_create_at.includes(this.searchKeyword)
          );
        } else {
          const value = manager[this.searchField];
          return value && value.toString().includes(this.searchKeyword);
        }
      });
    }
  }
}
</script>

<style scoped>
#managerSection {
  padding: 20px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

#headerContainer {
  width: 100%;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

#addManagerBtnContainer {
  margin-right: 20px;
}

.button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}

.button:hover {
  background-color: #5ea8da;
}

#searchContainer {
  display: flex;
  align-items: center;
}

#searchContainer input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  width: 250px;
}

#searchContainer select {
  margin-left: 10px;
  padding: 5px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.manager-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 15px;
  color: #333;
}

.manager-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.04);
}

.manager-table th,
.manager-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.manager-table th {
  font-weight: 600;
  color: #555;
}

.manager-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.manager-table tbody tr:hover {
  background-color: #f0f0f0;
  transition: background-color 0.3s ease;
}

.manager-table tbody td:last-child {
  text-align: center;
}

.delete-button {
  background-color: #f44336;
}

.delete-button:hover {
  background-color: #d32f2f;
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
  margin: auto;
  padding: 20px;
  border: 1px solid #888;
  width: 60%;
  max-width: 600px;
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
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.submit-button,
.cancel-button {
  padding: 10px 15px;
  margin-top: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.submit-button {
  background-color: #5ea8da;
  color: white;
  margin-right: 10px;
}

.submit-button:hover {
  background-color: #5ea8da;
}

.cancel-button {
  background-color: #f44336;
  color: white;
}

.cancel-button:hover {
  background-color: #d32f2f;
}
</style>