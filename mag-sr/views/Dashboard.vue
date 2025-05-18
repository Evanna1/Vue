<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <Sidebar 
        @show-profile="showSection('profile')" 
        @show-managers="showSection('managers')" 
        @show-users="showSection('users')" 
        @show-articles="showSection('articles')" 
      />
      
      <div class="dashboard-content">
        <Profile 
          v-if="currentView === 'profile'"
          :profile="profile" 
          @profile-updated="loadProfile"
        />
        <UserTable 
          v-if="currentView === 'users'" 
          :users="users" 
          @refresh-users="loadUsers"
          />
        <div v-if="currentView === 'managers' && isAdmin">
          <ManagerTable 
            :managers="managers" 
            @delete-manager="deleteManager" 
            @add-manager="addManager"
            @refresh-managers="loadManagers" 
          />
        </div>
        <div v-if="currentView === 'managers' && !isAdmin">
          <p>权限不足，无法查看管理员列表</p>
        </div>
        <ArticleTable 
          v-if="currentView === 'articles'" 
          :articles="articles" 
          @change-permission="changeArticlePermission"
          @refresh-articles="loadArticles"
        />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Sidebar from '../components/Sidebar.vue';
import Profile from '../components/Profile.vue';
import UserTable from '../components/UserTable.vue';
import ManagerTable from '../components/ManagerTable.vue';
import ArticleTable from '../components/ArticleTable.vue';

export default {
  components: {
    Sidebar,
    Profile,
    UserTable,
    ManagerTable,
    ArticleTable
  },
  data() {
    return {
      currentView: 'profile',
      profile: {},
      users: [],
      managers: [],
      articles: [],
      isAdmin: false // 用于标识是否为超级管理员
    };
  },
  created() {
    console.log('Dashboard created');
    this.loadProfile();
    this.checkAdminStatus(); // 检查是否为超级管理员
  },
  methods: {
    showSection(section) {
      if (section === 'managers' && !this.isAdmin) {
        alert('权限不足，无法查看管理员列表');
        return;
      }
      this.currentView = section;
      this.loadDataForSection(section);
    },
    checkAdminStatus() {
      // 获取当前登录的管理员id
      const currentMngId = localStorage.getItem('currentMngId');
      if (currentMngId) {
        this.isAdmin = currentMngId === '1'; // 假设超级管理员的ID是字符串"1"
      } else {
        // 尝试从profile中获取ID
        if (this.profile && this.profile.mng_id) {
          this.isAdmin = this.profile.mng_id === 1;
        } else {
          this.isAdmin = false;
        }
      }
    },
    loadDataForSection(section) {
      switch(section) {
        case 'profile':
          this.loadProfile();
          break;
        case 'managers':
          if (this.isAdmin) {
            this.loadManagers();
          } else {
            alert('权限不足，无法查看管理员列表');
          }
          break;
        case 'users':
          this.loadUsers();
          break;
        case 'articles':
          this.loadArticles();
          break;
      }
    },
    async loadProfile() {
      try {
        const token = localStorage.getItem('token'); 
        const response = await axios.get('http://localhost:5000/manager/profile', {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        const data = response.data;
        if (data.state === 1) {
          this.profile = data.profile;
          // 如果profile加载成功且之前没有检查过管理员状态，再检查一次
          if (this.isAdmin === false && this.profile.mng_id) {
            this.isAdmin = this.profile.mng_id === 1;
          }
        } else {
          console.error('获取管理员信息失败:', data.message);
        }
      } catch (error) {
        console.error('请求管理员信息接口失败:', error);
      }
    },
    async loadManagers() {
      if (!this.isAdmin) {
        alert('权限不足，无法查看管理员列表');
        return;
      }
      try {
        const token = localStorage.getItem('token'); 
        const response = await axios.get('http://localhost:5000/manager/manager_list', {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        const data = response.data;
        if (data.state === 1) {
          this.managers = data.managers;
        } else {
          console.error('获取管理员列表失败:', data.message);
        }
      } catch (error) {
        console.error('请求管理员列表接口失败:', error);
      }
    },
    async loadUsers() {
      try {
        const token = localStorage.getItem('token'); 
        const response = await axios.get('http://localhost:5000/manager/user_list', {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        const data = response.data;
        console.log(data)
        if (data.state === 1) {
          this.users = data.users;
        } else {
          console.error('获取用户列表失败:', data.message);
        }
      } catch (error) {
        console.error('请求用户列表接口失败:', error);
      }
    },
    async loadArticles() {
      try {
        const token = localStorage.getItem('token'); 
        const response = await axios.get('http://localhost:5000/manager/article_list', {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        const data = response.data;
        console.log(data)
        if (data.state === 1) {
          this.articles = data.articles; // 将文章数据赋值给 this.articles
        } else {
          console.error('获取文章列表失败:', data.message);
        }
      } catch (error) {
        console.error('请求文章列表接口失败:', error);
      }
    }
  }
}
</script>
<style scoped>
.dashboard-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #e0e7ef;
  display: flex;
  justify-content: flex-start;
  align-items: stretch;
  padding-left: 0;
}

.dashboard-container {
  display: flex;
  width: 100%;
  height: 100%;
  border-radius: 0;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(219, 11, 11, 0.1);
  background-color: #fff;
}

/* Sidebar 左侧栏 */
.sidebar {
  width: 260px;
  background-color: #2c3e50;
  color: white;
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 内容区域 */
.dashboard-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  background-color: #f9fbfd;
  height: 100%;
}
</style>