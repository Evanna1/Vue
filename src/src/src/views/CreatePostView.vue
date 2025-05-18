<template>
  <router-link to="/" class="logo-absolute">NexTecht</router-link>
  <div class="create-post-container">
    <div class="header-bar">
      <h1 class="page-title">博客创作</h1>
      </div>

    <div class="form-card privacy-toggle-section">
      <label for="isPrivateToggleInput">是否私密</label>
      <label class="switch">
        <input type="checkbox" id="isPrivateToggleInput" v-model="isPrivate" />
        <span class="slider"></span>
      </label>
    </div>
    <div class="form-card">
      <label for="title">标题</label>
      <input
        v-model="title"
        @input="titleError = false"
        :class="['input-field', titleError ? 'error' : '']"
        id="title"
        placeholder="请输入博客标题"
      />
      <p v-if="titleError" class="error-text">标题不能为空</p>
    </div>

    <div class="form-card">
      <label for="tags">标签</label>
      <input
        v-model="tags"
        id="tags"
        placeholder="用逗号分隔，如：前端,Vue,生活"
        class="input-field"
      />
    </div>

    <div class="form-card">
      <label>封面图（可选）</label>
      <input type="file" @change="handleCoverUpload" accept="image/*" class="input-field" />
      <img v-if="coverPreview" :src="coverPreview" class="cover-preview" />
    </div>

    <div class="form-card">
      <label>内容</label>
      <div class="editor-container" :class="{ error: contentError }">
        <Toolbar
          style="border-bottom: 1px solid #ccc"
          :editor="editorRef"
          :defaultConfig="toolbarConfig"
          mode="default"
        />
        <Editor
          style="height: 400px; overflow-y: auto"
          v-model="htmlContent"
          :defaultConfig="editorConfig"
          mode="default"
          @onCreated="handleCreated"
          @onChange="handleContentInput"
        />
      </div>
      <p v-if="contentError" class="error-text">内容不能为空</p>
    </div>

    <div class="button-group">
      <button class="publish-btn" @click="publishPost">发布</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, shallowRef, onBeforeUnmount } from 'vue'
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const title = ref('')
const tags = ref('')
const htmlContent = ref('')
const coverPreview = ref<string | null>(null)
let coverFile: File | null = null

const titleError = ref(false)
const contentError = ref(false)

const isPrivate = ref(false) // This existing ref will be used by the new toggle

const editorRef = shallowRef()
const toolbarConfig = {}
const editorConfig = {
  placeholder: '请输入内容...',
  MENU_CONF: {
    uploadImage: {
      server: 'http://127.0.0.1:5000/upload/image', // 你的 Flask 上传图片接口
      fieldName: 'image',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
      },
      customInsert(res: any, insertFn: Function) {
        // 后端返回的是 image_path: "/img/xxx.jpg"
        const imageUrl = res.image_path
        insertFn(imageUrl)  // 直接插入到光标处
      }
    }
  }
}

function handleCoverUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) {
    coverFile = file
    coverPreview.value = URL.createObjectURL(file)
  }
}

function handleCreated(editor: any) {
  editorRef.value = editor
}

function handleContentInput() {
  const html = editorRef.value?.getHtml() || ''
  if (html && html !== '<p><br></p>') {
    contentError.value = false
  }
}

onBeforeUnmount(() => {
  if (editorRef.value) {
    editorRef.value.destroy()
  }
})

async function publishPost() {
  if (!title.value.trim()) {
    titleError.value = true
    return
  }

  const html = editorRef.value?.getHtml() || ''
  if (!html || html === '<p><br></p>') {
    contentError.value = true
    return
  }

  const token = localStorage.getItem('token')
  if (!token) {
    alert('请先登录')
    router.push('/login')
    return
  }

  const formData = new FormData()
  formData.append('title', title.value)
  formData.append('content', html)
  formData.append('permission', isPrivate.value ? '1' : '0')
  formData.append('tag', tags.value.trim())
  // Append tags if you have a field for it in the backend and want to include it
  // formData.append('tags', tags.value);


  if (coverFile) {
    formData.append('cover', coverFile)
  }

  try {
    const response = await axios.post(
      'http://127.0.0.1:5000/article/create',
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          // axios 会自动设置 multipart/form-data 和边界
        },
      }
    )

    alert('发布成功！')
    router.push('/')
  } catch (error: any) {
    if (error.response) {
      alert(error.response.data.message || '发布失败')
    } else {
      alert('网络错误或服务器异常')
    }
  }
}
</script>

<style scoped>
.logo-absolute {
  position: absolute;
  top: 20px;
  left: 30px;
  font-family: 'Great Vibes', cursive;
  font-size: 42px;
  font-weight: bold;
  color: #0077cc;
  text-decoration: none;
  z-index: 1000;
}
.create-post-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 16px;
  font-family: 'Helvetica Neue', sans-serif;
  background-color: #fff; /* Changed to #fff to match form-card background or make it distinct if preferred */
}

.header-bar {
  display: flex;
  justify-content: center; /* 让“博客创作”居中 */
  align-items: center;
  margin-bottom: 24px;
  position: relative;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  color: #333;
}

.form-card {
  background: #fff;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

/* NEW STYLES FOR THE PRIVACY TOGGLE SECTION */
.privacy-toggle-section {
  flex-direction: row;           /* Override .form-card's column direction */
  justify-content: space-between;/* "是否私密" label on left, switch on right */
  align-items: center;           /* Vertically center items in the row */
}

/* Style for the text label "是否私密" within the new section */
.privacy-toggle-section > label[for="isPrivateToggleInput"] {
  margin-bottom: 0; /* Remove default bottom margin from general label style */
  /* display: block; is default for label, but flex item behavior will manage it */
}

/* Style for the switch component within the new section */
.privacy-toggle-section > .switch {
  margin-top: 0; /* Remove default top margin from general switch style */
}
/* END OF NEW STYLES */

label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  display: block;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 8px;
  margin-top: 6px;
  background-color: #f7f7f7;
  box-sizing: border-box;
}

.cover-preview {
  margin-top: 10px;
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.editor-container {
  border: 1px solid #ccc;
  border-radius: 8px;
  background: #fff;
  margin-top: 6px;
}

.button-group {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.publish-btn {
  background: #2f80ed;
  color: #fff;
  padding: 12px 24px;
  font-size: 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.publish-btn:hover {
  background: #1c63d2;
}

.error {
  border: 1px solid #e74c3c !important;
  box-shadow: 0 0 5px rgba(231, 76, 60, 0.5);
}

.error-text {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 6px;
}

/* 响应式 */
@media (max-width: 600px) {
  .page-title {
    font-size: 22px;
  }
  .form-card {
    padding: 16px;
  }
  .publish-btn {
    width: 100%;
    text-align: center;
  }
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px; /* Adjusted for better visual balance with 28px height */
  height: 28px; /* Adjusted for better visual balance */
  /* margin-top: 8px; Removed as specific section will handle margins */
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0;
  right: 0; bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 28px; /* Match height */
}
.slider:before {
  position: absolute;
  content: "";
  height: 20px; /* Smaller than slider height */
  width: 20px;  /* Smaller than slider height */
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: #4caf50; /* Green for checked */
}
input:checked + .slider:before {
  transform: translateX(22px); /* (Switch width - knob width - 2*offset) = 50 - 20 - 2*4 = 22, or adjust as needed */
}
</style>