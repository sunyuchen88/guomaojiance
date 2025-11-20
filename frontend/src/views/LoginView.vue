<template>
  <div class="login-container">
    <a-card class="login-card" title="食品质检系统">
      <a-form
        :model="formState"
        :rules="rules"
        @finish="handleLogin"
        layout="vertical"
      >
        <a-form-item label="用户名" name="username">
          <a-input
            v-model:value="formState.username"
            placeholder="请输入用户名"
            size="large"
            :disabled="loading"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item label="密码" name="password">
          <a-input-password
            v-model:value="formState.password"
            placeholder="请输入密码"
            size="large"
            :disabled="loading"
          >
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            block
            size="large"
            :loading="loading"
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>

      <div class="login-footer">
        <p>默认账号: admin / admin123</p>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message } from 'ant-design-vue';
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue';
import { useUserStore } from '@/stores/user';
import { login as loginApi } from '@/services/authService';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const formState = reactive({
  username: '',
  password: '',
});

const loading = ref(false);

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8个字符', trigger: 'blur' },
  ],
};

async function handleLogin() {
  loading.value = true;

  try {
    const response = await loginApi({
      username: formState.username,
      password: formState.password,
    });

    // Store user and token
    userStore.setUser(response.user);
    userStore.setToken(response.access_token);

    message.success('登录成功');

    // Redirect to the page user was trying to access, or dashboard
    const redirect = (route.query.redirect as string) || '/';
    router.push(redirect);
  } catch (error: any) {
    console.error('Login error:', error);
    // Error message will be handled by axios interceptor
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-card :deep(.ant-card-head-title) {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
}

.login-footer {
  margin-top: 16px;
  text-align: center;
  color: #999;
  font-size: 12px;
}
</style>
