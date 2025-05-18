<template>
  <div class="login-wrapper">
    <div class="login-container">
      <h2>管理员登录</h2>
      <div class="form-group">
        <input
          type="text"
          v-model="account"
          placeholder="账号 / 姓名 / 邮箱 / 电话"
        />
      </div>
      <div class="form-group">
        <input
          type="password"
          v-model="password"
          placeholder="密码"
        />
      </div>
      <button @click="handleLogin">登录</button>
      <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminLogin',
  data() {
    return {
      account: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
    async handleLogin() {
      if (!this.account || !this.password) {
        this.errorMessage = '请填写所有字段';
        return;
      }

      try {
        const response = await axios.post('http://localhost:5000/manager/login', {
          m_account: this.account,
          m_password: this.password
        });

        const data = response.data; // axios 自动解析 JSON

        if (data.state === 1) {
          localStorage.setItem('token', data.token);
          this.$router.push('/bashbord'); // 登录成功跳转后台
        } else {
          this.errorMessage = data.message;
        }
      } catch (error) {
        console.error('请求出错:', error);
        this.errorMessage = '网络错误，请重试';
      }
    }
  }
};
</script>

<style scoped>
body, html {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(to right, #74ebd5, #acb6e5);
}

.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 90vw;
  height: 100vh;
  box-sizing: border-box;
}

.login-container {
  background-color: #ffffff;
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
  width: 340px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-container h2 {
  margin-bottom: 25px;
  color: #333;
}

.form-group {
  margin-bottom: 18px;
  width: 100%;
}

input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s, box-shadow 0.3s;
}

input:focus {
  border-color: #4CAF50;
  box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
  outline: none;
}

button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  background-color: #4CAF50;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s;
}

button:hover {
  background-color: #43a047;
  transform: scale(1.03);
}

.error-message {
  color: #e53935;
  margin-top: 15px;
  font-size: 14px;
  text-align: center;
}
</style>
