<template>
  <router-link to="/" class="logo-absolute">NexTecht</router-link>
  <div class="post-detail-container">

    <div class="card title-card">
      <h1 class="post-title">{{ post.title }}</h1>
      <div class="post-meta" v-if="post.author">
        <span>作者: {{ post.author }}</span>
        <span>创建时间: {{ formatDate(post.create_time) }}</span>
        <span v-if="post.update_time">更新时间: {{ formatDate(post.update_time) }}</span>
         <span v-if="post.read_count !== undefined && post.read_count !== null">阅读量: {{ post.read_count }}</span>
      </div>
    </div>

    <div class="card content-card">
      <div class="post-content" v-html="post.content"></div>
    </div>

    <div class="card interaction-card">
      <div class="interaction-buttons">
        <button @click="handleArticleLike" class="interaction-button like-button">
          ❤️ 喜欢 ({{ post.like_count || 0 }})
        </button>
        <button @click="handleArticleFavorite" class="interaction-button favorite-button">
          ⭐ 收藏 ({{ post.favorite_count || 0 }})
        </button>
      </div>
       <p class="interaction-note">(文章点赞和收藏功能暂未开放)</p>
    </div>

    <div class="card comments-card">
      <h2 class="comments-title">评论区</h2>

      <div class="add-comment-form">
          <textarea
              v-model="newCommentContent"
              :placeholder="replyingTo ? `回复 ${replyingTo.user.username}:` : '发表评论...'"
              rows="4"
              ref="commentInput"
          ></textarea>
          <div class="form-actions">
              <button v-if="replyingTo" @click="cancelReply" class="cancel-reply-button">取消回复</button>
              <button @click="submitComment" :disabled="!newCommentContent.trim()">发送</button>
          </div>
      </div>

      <div class="comment-list">
           <div v-if="loadingComments" class="loading-comments">
               加载评论中...
           </div>
          <div v-if="comments.length === 0 && !loadingComments" class="comments-placeholder">
              暂无评论，快来发表第一条评论吧！
          </div>


          <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-meta">
                  <span class="comment-author">{{ comment.user?.username || 'Deleted User' }}</span>
                  <span class="comment-time">{{ formatDate(comment.create_time) }}</span>
              </div>
              <div class="comment-content">
                  <p>{{ comment.content }}</p>
              </div>
              <div class="comment-actions">
                  <button @click="startReply(comment)" class="action-button reply-button">回复 ({{ comment.reply_count || 0 }})</button>
                  <button @click="toggleLikeComment(comment)" class="action-button like-button" :class="{ 'liked': comment.is_liked }">
                      ❤️ {{ comment.like_count || 0 }}
                  </button>
                  <button @click="reportComment(comment.id)" class="action-button report-button">举报</button>
                  <button v-if="currentUserId && comment.user?.id === currentUserId" @click="deleteComment(comment.id)" class="action-button delete-button">删除</button>
              </div>

              <div v-if="comment.reply_count > 0" class="replies-section">
                   <button v-if="!comment.showReplies && !comment.loadingReplies" @click="fetchReplies(comment)" class="load-replies-button">
                       查看全部 {{ comment.reply_count }} 条回复
                   </button>
                   <button v-if="comment.showReplies && comment.replies && comment.replies.length > 0" @click="comment.showReplies = false" class="load-replies-button">
                        收起回复
                   </button>
                   <div v-if="comment.loadingReplies" class="loading-replies">加载中...</div>

                  <div v-if="comment.showReplies && comment.replies && comment.replies.length > 0" class="reply-list">
                      <div v-for="reply in comment.replies" :key="reply.id" class="comment-item reply-item">
                          <div class="comment-meta">
                              <span class="comment-author">{{ reply.user?.username || 'Deleted User' }}</span>
                              <span class="comment-time">{{ formatDate(reply.create_time) }}</span>
                          </div>
                          <div class="comment-content">
                               <span v-if="reply.parent_id" class="reply-to">
                                     回复 @{{ getParentAuthorUsername(reply.parent_id) }}:
                                </span>
                              {{ reply.content }}
                          </div>
                           <div class="comment-actions">
                               <button @click="toggleLikeComment(reply)" class="action-button like-button" :class="{ 'liked': reply.is_liked }">
                                   ❤️ {{ reply.like_count || 0 }}
                               </button>
                               <button @click="reportComment(reply.id)" class="action-button report-button">举报</button>
                               <button v-if="currentUserId && reply.user?.id === currentUserId" @click="deleteComment(reply.id)" class="action-button delete-button">删除</button>
                           </div>
                      </div>
                  </div>
              </div>
          </div>
      </div>

      <div v-if="pagination.total_pages > 1 && !loadingComments" class="comments-pagination">
          <button @click="goToPage(pagination.current_page - 1)" :disabled="pagination.current_page === 1">上一页</button>
          <span>第 {{ pagination.current_page }} / {{ pagination.total_pages }} 页</span>
          <button @click="goToPage(pagination.current_page + 1)" :disabled="pagination.current_page === pagination.total_pages">下一页</button>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'; // Import nextTick
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { format } from 'date-fns';

// 定义文章数据的响应式引用
const post = ref({
  id: null as number | null,
  title: '',
  content: '',
  author: '', // 作者用户名
  create_time: null as string | null, // 创建时间
  update_time: null as string | null, // 更新时间
  read_count: 0, // 阅读量
  like_count: 0, // 文章喜欢数
  favorite_count: 0, // 文章收藏数
});

// 定义评论的数据结构和响应式引用
interface Comment {
    id: number;
    content: string;
    article_id: number;
    create_time: string | null;
    update_time: string | null;
    status: number; // 评论状态 (0:正常, 1:已删除, 2:屏蔽, 3:举报)
    is_approved: number; // 审核状态 (0:待审核, 1:已通过, 2:未通过) - 注意这是 number 根据你的DB
    like_count: number; // 评论点赞数
    reply_count: number; // 子评论数
    depth: number; // 评论层级 (1为顶级，2为子评论)
    parent_id: number | null; // 父评论ID
    user: { // 嵌套的用户信息
        id: number;
        username: string;
        nickname: string;
        avatar: string;
    };
    is_liked?: boolean; // 当前用户是否已点赞该评论 (来自后端接口)
    replies?: Comment[]; // 用于存储子评论
    showReplies?: boolean; // 用于控制子评论的展开/收起
    loadingReplies?: boolean; // 用于表示子评论正在加载中
}

const comments = ref<Comment[]>([]); // 存储顶级评论列表
const newCommentContent = ref(''); // 评论输入框内容
const replyingTo = ref<Comment | null>(null); // 当前回复的目标评论
const pagination = ref({ // 评论分页信息
    current_page: 1,
    total_pages: 1,
    total_items: 0,
    per_page: 10,
});
const loadingComments = ref(false); // 加载顶级评论状态

const route = useRoute();
const router = useRouter();

// 获取当前登录用户的 ID。这通常从登录成功后存储在 localStorage, Vuex 或 Pinia 中的用户信息获取
const currentUserId = ref<number | null>(null);
// 引用评论输入框 DOM 元素
const commentInput = ref<HTMLTextAreaElement | null>(null);


// 辅助函数：格式化日期字符串
const formatDate = (dateString: string | null): string => {
  if (!dateString) {
    return '未知时间';
  }
  try {
    return format(new Date(dateString), 'yyyy-MM-dd HH:mm:ss');
  } catch (e) {
    console.error("Error formatting date:", e);
    return dateString;
  }
};

// 辅助函数：根据父评论ID获取父评论的作者用户名 (用于子评论显示 "回复@...")
const getParentAuthorUsername = (parent_id: number | null): string => {
    if (!parent_id) return '未知用户';
    // 在已加载的顶级评论中查找父评论
    const parent = comments.value.find(c => c.id === parent_id);
    return parent?.user?.username || '未知用户';
};


// 获取评论列表 (顶级评论，带分页)
const fetchComments = async (page: number = 1) => {
  const articleId = route.params.id;
   if (!articleId || typeof articleId !== 'string') return; // Ensure articleId is string for API

   loadingComments.value = true; // 开始加载
  try {
    const response = await axios.get(`http://127.0.0.1:5000/article/${articleId}/comments`, {
      headers: {
        // 在请求头中携带 Authorization，即使是可选登录，后端也可能需要
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      params: { // 添加分页参数
          page: page,
          per_page: pagination.value.per_page // 使用当前每页数量
      }
    });

    if (response.data.state === 1) {
      // 将获取到的顶级评论赋值给 comments 列表
      // 为每个顶级评论初始化 replies 数组, showReplies 状态 和 loadingReplies 状态
      comments.value = response.data.comments.map((comment: Comment) => ({
          ...comment,
          replies: [], // 初始化子评论数组
          showReplies: false, // 初始化子评论展开状态
          loadingReplies: false, // 初始化子评论加载状态
      }));

      // 更新分页信息
      pagination.value.current_page = response.data.current_page;
      pagination.value.total_pages = response.data.total_pages;
      pagination.value.total_items = response.data.total_items;
      pagination.value.per_page = response.data.per_page;

    } else {
      console.error('Error fetching comments: Invalid response state', response.data);
      alert("加载评论失败: " + (response.data.message || "未知错误"));
       comments.value = []; // 清空评论列表
        pagination.value = { current_page: 1, total_pages: 1, total_items: 0, per_page: 10 };
    }

  } catch (error) {
    console.error('Error fetching comments:', error);
     if (axios.isAxiosError(error) && error.response) {
         // 处理具体的HTTP错误
         alert("加载评论失败：" + (error.response.data?.message || error.message));
     } else {
         alert("加载评论失败：" + (error instanceof Error ? error.message : String(error)));
     }
     comments.value = []; // 清空评论列表
     pagination.value = { current_page: 1, total_pages: 1, total_items: 0, per_page: 10 };
  } finally {
      loadingComments.value = false; // 结束加载
  }
};

// 获取子评论列表
const fetchReplies = async (parentComment: Comment) => {
     if (!parentComment || parentComment.reply_count === 0) return;

     // 避免重复加载，如果已经加载且显示，则收起
     if (parentComment.replies && parentComment.replies.length > 0 && parentComment.showReplies) {
         parentComment.showReplies = false;
         return;
     }
      // 如果已经加载但未显示，则直接显示
     if (parentComment.replies && parentComment.replies.length > 0 && !parentComment.showReplies) {
          parentComment.showReplies = true;
          return;
     }


     parentComment.loadingReplies = true; // 开始加载子评论
     try {
         const response = await axios.get(`http://127.0.0.1:5000/comment/${parentComment.id}/replies`, {
             headers: {
                // 在请求头中携带 Authorization，即使是可选登录
                Authorization: `Bearer ${localStorage.getItem('token')}`,
             }
         });

         if (response.data.state === 1) {
             // 将获取到的子评论赋值给对应父评论的 replies 数组
             parentComment.replies = response.data.replies;
             parentComment.showReplies = true; // 展开子评论列表
         } else {
             console.error('Error fetching replies: Invalid response state', response.data);
             alert("加载回复失败: " + (response.data.message || "未知错误"));
             parentComment.replies = []; // 清空或设置为默认
         }

     } catch (error) {
         console.error('Error fetching replies:', error);
         if (axios.isAxiosError(error) && error.response) {
             alert("加载回复失败：" + (error.response.data?.message || error.message));
         } else {
             alert("加载回复失败：" + (error instanceof Error ? error.message : String(error)));
         }
         parentComment.replies = []; // 清空或设置为默认
     } finally {
         parentComment.loadingReplies = false; // 结束加载子评论
     }
};


// 提交评论或回复
const submitComment = async () => {
  const articleId = route.params.id;
  if (!articleId || typeof articleId !== 'string') return;
  if (!newCommentContent.value.trim()) return; // 检查文章ID和内容

  // 检查是否登录
  if (!currentUserId.value) {
      alert("请先登录才能发表评论！");
      router.push('/login');
      return;
  }

  const payload: { content: string; parent_id?: number } = {
      content: newCommentContent.value.trim()
  };

  // 如果是回复，添加 parent_id
  if (replyingTo.value) {
      payload.parent_id = replyingTo.value.id;
  }

  try {
    const response = await axios.post(`http://127.0.0.1:5000/comment/${articleId}/create`, payload, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.data.state === 1) {
      alert("评论发表成功！");
      newCommentContent.value = ''; // 清空输入框
      replyingTo.value = null; // 取消回复状态

      // 成功后刷新当前页评论列表，以显示新评论
      fetchComments(pagination.value.current_page);

    } else {
      console.error('Error submitting comment: Invalid response state', response.data);
      alert("评论发表失败：" + (response.data.message || "未知错误"));
    }

  } catch (error) {
    console.error('Error submitting comment:', error);
    if (axios.isAxiosError(error) && error.response) {
         if (error.response.status === 401) {
              alert("请先登录才能发表评论！");
              router.push('/login');
         } else {
             alert("评论发表失败：" + (error.response.data?.message || error.message));
         }
     } else {
         alert("评论发表失败：" + (error instanceof Error ? error.message : String(error)));
     }
  }
};

// 开始回复某个评论
const startReply = (comment: Comment) => {
    replyingTo.value = comment;
    newCommentContent.value = ''; // 清空当前输入，准备回复
    // 确保输入框 DOM 存在，然后聚焦
    nextTick(() => {
        if (commentInput.value) {
            commentInput.value.focus();
        }
    });

    // 同时获取并显示该评论的子评论
    fetchReplies(comment);
};

// 取消回复
const cancelReply = () => {
    replyingTo.value = null;
    newCommentContent.value = ''; // 清空输入
};


// 切换评论的点赞状态 (根据后端返回的 is_liked 和 like_count 更新前端)
const toggleLikeComment = async (comment: Comment) => {
     if (!currentUserId.value) {
         alert("请先登录才能点赞评论！");
         router.push('/login');
         return;
     }

     const url = comment.is_liked // 根据当前状态判断调用点赞还是取消点赞接口
         ? `http://127.0.0.1:5000/comment/unlike/${comment.id}`
         : `http://127.0.0.1:5000/comment/like/${comment.id}`;

     try {
         const response = await axios.post(url, {}, {
             headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`,
             }
         });

         // 后端接口返回 updated count 和 is_liked
         if (response.data.state === 1 || response.data.state === 0) { // 即使 state=0 (Already liked/Not liked yet) 也更新前端状态
             comment.like_count = response.data.like_count;
             comment.is_liked = response.data.is_liked; // 直接使用后端返回的最新状态
             console.log(response.data.message);
         } else {
              console.error('Error toggling comment like: Invalid response state', response.data);
             alert("操作失败：" + (response.data.message || "未知错误"));
         }

     } catch (error) {
          console.error('Error toggling comment like:', error);
          if (axios.isAxiosError(error) && error.response) {
             if (error.response.status === 401) {
                  alert("请先登录才能点赞评论！");
                  router.push('/login');
             } else {
                 alert("操作失败：" + (error.response.data?.message || error.message));
             }
         } else {
             alert("操作失败：" + (error instanceof Error ? error.message : String(error)));
         }
     }
};

// 举报评论
const reportComment = async (commentId: number) => {
     if (!confirm("确定要举报这条评论吗？")) {
         return;
     }
      if (!currentUserId.value) {
         alert("请先登录才能举报评论！");
         router.push('/login');
         return;
     }
     try {
         const response = await axios.post(`http://127.0.0.1:5000/comment/report/${commentId}`, {}, {
              headers: {
                 Authorization: `Bearer ${localStorage.getItem('token')}`,
             }
         });

         if (response.data.state === 1) {
             alert("评论举报成功！感谢您的反馈。");
             // TODO: 根据需要处理前端显示，例如如果举报后评论被隐藏，可以从列表中移除
             // 简单处理：如果举报成功，可以在前端将该评论标记为已举报状态 (如果 Comment 接口返回举报状态的话)
             // let commentToReport = comments.value.find(c => c.id === commentId);
             // if (commentToReport) commentToReport.status = 3; // 假设 3 是举报状态
             // 还需要检查子评论
              comments.value.forEach(c => {
                 if (c.id === commentId) c.status = 3;
                 if (c.replies) {
                     c.replies.forEach(r => {
                         if (r.id === commentId) r.status = 3;
                     });
                 }
             });

         } else {
             console.error('Error reporting comment: Invalid response state', response.data);
             alert("举报失败：" + (response.data.message || "未知错误"));
         }

     } catch (error) {
          console.error('Error reporting comment:', error);
          if (axios.isAxiosError(error) && error.response) {
             if (error.response.status === 401) {
                  alert("请先登录才能举报评论！");
                  router.push('/login');
             } else {
                 alert("举报失败：" + (error.response.data?.message || error.message));
             }
         } else {
             alert("举报失败：" + (error instanceof Error ? error.message : String(error)));
         }
     }
};

// 删除评论
const deleteComment = async (commentId: number) => {
     if (!confirm("确定要删除这条评论吗？")) {
         return;
     }
      if (!currentUserId.value) {
         alert("请先登录才能删除评论！");
         router.push('/login');
         return;
     }
     try {
         const response = await axios.delete(`http://127.0.0.1:5000/comment/delete/${commentId}`, {
              headers: {
                 Authorization: `Bearer ${localStorage.getItem('token')}`,
             }
         });

         if (response.data.state === 1) {
             alert("评论删除成功！");
             // 从列表中移除被删除的评论
             let found = false;
             // 尝试在顶级评论中查找并移除
             comments.value = comments.value.filter(comment => {
                 if (comment.id === commentId) {
                     found = true;
                     return false; // 移除这个顶级评论
                 }
                 // 尝试在子评论中查找并移除
                 if (comment.replies) {
                     const initialReplyCount = comment.replies.length;
                     comment.replies = comment.replies.filter(reply => {
                         if (reply.id === commentId) {
                             found = true;
                             return false; // 移除这个子评论
                         }
                         return true;
                     });
                     // 如果删除了子评论，更新父评论的 reply_count
                     if (comment.replies.length < initialReplyCount) {
                        comment.reply_count = comment.reply_count > 0 ? comment.reply_count - 1 : 0; // 乐观更新计数
                     }
                 }
                 return true; // 保留这个顶级评论
             });


         } else {
             console.error('Error deleting comment: Invalid response state', response.data);
             alert("删除失败：" + (response.data.message || "未知错误"));
         }

     } catch (error) {
          console.error('Error deleting comment:', error);
          if (axios.isAxiosError(error) && error.response) {
             if (error.response.status === 401) {
                  alert("请先登录或您无权删除此评论！");
                  router.push('/login');
             } else if (error.response.status === 403) {
                  alert("您无权删除此评论！");
             }
             else {
                 alert("删除失败：" + (error.response.data?.message || error.message));
             }
         } else {
             alert("删除失败：" + (error instanceof Error ? error.message : String(error)));
         }
     }
};


// 分页跳转
const goToPage = (page: number) => {
    if (page >= 1 && page <= pagination.value.total_pages && page !== pagination.value.current_page) {
        fetchComments(page);
         // 滚动到评论区顶部
         nextTick(() => { // 确保DOM更新后滚动
             document.querySelector('.comments-card')?.scrollIntoView({ behavior: 'smooth' });
         });
    }
};

// 占位符函数：处理文章点赞 (保留原逻辑)
const handleArticleLike = () => {
  alert("文章点赞功能暂未开放！");
};

// 占位符函数：处理文章收藏 (保留原逻辑)
const handleArticleFavorite = () => {
   alert("文章收藏功能暂未开放！");
};


// 原始的 goBack 函数 (保留)
function goBack() {
  router.push('/profile');
}

onMounted(async () => {
  const postId = route.params.id;
   if (!postId || typeof postId !== 'string') {
       console.error("Article ID is missing!");
       return;
   }

   // 尝试获取当前用户 ID (在实际应用中确保这是正确的获取方式)
   const userId = localStorage.getItem('user_id'); // 假设登录时存储了 userId
    if (userId) {
        currentUserId.value = parseInt(userId, 10);
    }


  try {
    // 1. 加载文章详情
    const articleResponse = await axios.get(`http://127.0.0.1:5000/user/article_content/${postId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });

    console.log("Article API Response:", articleResponse.data);

    if (articleResponse.data.state === 1 && articleResponse.data.article) {
      post.value = {
        ...post.value,
        ...articleResponse.data.article,
      };
    } else {
         console.error('Error fetching post details: Invalid response state', articleResponse.data);
         alert("加载文章失败：" + (articleResponse.data.message || "未知错误"));
         router.push('/profile');
         return; // 文章加载失败则不继续加载评论
    }

    // 2. 文章加载成功后，加载评论
    fetchComments(1); // 加载第一页顶级评论

  } catch (error) {
    console.error('Error fetching initial data:', error); // Changed log message
     if (axios.isAxiosError(error) && error.response) {
         if (error.response.status === 404) {
             alert("文章未找到！");
             router.push('/profile');
         } else if (error.response.status === 401) {
              alert("请先登录！");
              router.push('/login');
         } else {
             alert("加载失败：" + (error.response.data?.message || error.message));
         }
     } else {
         alert("加载失败：" + (error instanceof Error ? error.message : String(error)));
     }
      // 即使加载文章失败，评论区也应显示无评论状态
       comments.value = [];
       pagination.value = { current_page: 1, total_pages: 1, total_items: 0, per_page: 10 };
  }
});


</script>

<style scoped>
/* 保留你原有的样式，并添加评论区的新样式 */
/* ... (你的所有原有样式) ... */

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
.post-detail-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
  font-family: 'Helvetica Neue', sans-serif;
}

.card {
 background: #fff;
 border-radius: 16px;
 box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
 padding: 30px;
 margin-bottom: 30px;
 transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
 transform: translateY(-2px);
}

.title-card {
 text-align: center;
}

.post-title {
 font-size: 32px;
 font-weight: 700;
 margin: 0;
 margin-bottom: 15px; /* Add space below title */
}

/* 添加元信息样式 */
.post-meta {
 font-size: 14px;
 color: #555;
 display: flex; /* 使用 flexbox 排列元素 */
 justify-content: center; /* 居中对齐 */
 gap: 20px; /* 设置元素之间的间隔 */
 flex-wrap: wrap; /* 允许换行 */
}

.post-meta span {
 /* 单个元信息项的样式 */
 white-space: nowrap; /* 防止单项内的文本换行 */
}


.content-card {
 line-height: 1.7;
 font-size: 16px;
 color: #333;
}

/* Your existing deep selector for blockquote */
.post-content >>> blockquote {
  margin-left: 0;
  padding-left: 1em;
  border-left: 4px solid #ccc;
  color: #555;
  font-style: italic;
}

/* 新增互动区样式 */
.interaction-card {
    text-align: center;
}

.interaction-buttons {
    display: flex;
    justify-content: center; /* 按钮居中 */
    gap: 30px; /* 按钮之间的间隔 */
    margin-bottom: 15px; /* 按钮下方留白 */
}

.interaction-button {
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    border: none;
    border-radius: 8px;
    transition: background-color 0.3s ease, transform 0.1s ease;
     display: flex; /* 使用 flexbox 方便图标和文字对齐 */
     align-items: center;
     gap: 8px; /* 图标和文字之间的间隔 */
}

.interaction-button:hover {
    transform: translateY(-1px);
}

.like-button {
     background-color: #ffebee; /* 淡红色背景 */
     color: #e53935; /* 红色文字 */
}

.like-button:hover {
    background-color: #ef9a9a; /* 悬停变深 */
}

.favorite-button {
    background-color: #fff9c4; /* 淡黄色背景 */
    color: #fbc02d; /* 黄色文字 */
}

.favorite-button:hover {
    background-color: #fff59d; /* 悬停变深 */
}

.interaction-note {
    font-size: 14px;
    color: #777;
    margin-top: 0;
}


/* 新增评论区样式 */
.comments-card {
    /* 继承 .card 的样式 */
}

.comments-title {
    font-size: 24px;
    font-weight: 600;
    margin-top: 0;
    margin-bottom: 20px;
    text-align: center;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee; /* 分隔标题和评论表单/列表 */
}

/* 评论表单样式 */
.add-comment-form {
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.add-comment-form textarea {
    width: 100%;
    padding: 15px;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 16px;
    resize: vertical; /* 允许垂直拖动 */
    box-sizing: border-box; /* 包含 padding 和 border */
    margin-bottom: 10px;
    transition: border-color 0.3s ease;
}

.add-comment-form textarea:focus {
    border-color: #0077cc;
    outline: none;
    box-shadow: 0 0 5px rgba(0, 119, 204, 0.3);
}

.form-actions {
    text-align: right; /* 按钮靠右 */
}

.form-actions button {
    padding: 10px 20px;
    font-size: 16px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    margin-left: 10px; /* 按钮之间间隔 */
}

.form-actions button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

.form-actions button:not(:disabled):hover {
     opacity: 0.9;
}

.form-actions button:last-child { /* 发送按钮 */
    background-color: #0077cc;
    color: white;
}

.cancel-reply-button {
    background-color: #f0f0f0;
    color: #333;
}


/* 评论列表样式 */
.comment-list {
    margin-top: 20px;
}

.comments-placeholder {
    text-align: center;
    color: #999;
    font-style: italic;
    padding: 20px 0;
}

.loading-comments, .loading-replies {
     text-align: center;
     color: #666;
     padding: 10px 0;
}


.comment-item {
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    background-color: #fafafa; /* 浅背景色区分评论 */
}

/* 子评论样式 */
.reply-item {
    margin-left: 20px; /* 缩进 */
    border-left: 3px solid #ddd; /* 左边框 */
    background-color: #f5f5f5; /* 更浅的背景色 */
    padding-left: 15px; /* 留出左边框空间 */
}

.comment-meta {
    font-size: 13px;
    color: #777;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between; /* 作者和时间靠两边 */
    align-items: center;
}

.comment-author {
    font-weight: bold;
    color: #555;
}

.comment-content p {
    margin: 0 0 10px 0;
    line-height: 1.6;
    word-wrap: break-word; /* 防止长单词溢出 */
}

.comment-actions {
    font-size: 13px;
    color: #777;
    display: flex;
    gap: 15px; /* 按钮之间的间隔 */
    align-items: center;
    margin-top: 10px;
}

.action-button {
    background: none;
    border: none;
    padding: 0;
    font-size: 13px;
    color: #777;
    cursor: pointer;
    transition: color 0.2s ease;
     display: flex; /* 允许图标和文字对齐 */
     align-items: center;
     gap: 4px;
}

.action-button:hover {
    color: #000;
    text-decoration: underline;
}

.action-button.like-button:hover {
    color: #e53935; /* 鼠标悬停在评论点赞按钮上变红 */
}
/* 已点赞状态 */
.action-button.like-button.liked {
    color: #e53935; /* 已点赞时红色 */
     font-weight: bold;
}


.action-button.reply-button:hover {
    color: #0077cc; /* 鼠标悬停在回复按钮上变蓝 */
}
.action-button.report-button:hover {
    color: #ff9800; /* 鼠标悬停在举报按钮上变橙 */
}
.action-button.delete-button:hover {
    color: #f44336; /* 鼠标悬停在删除按钮上变红 */
}

.reply-to {
     font-weight: bold;
     color: #0077cc; /* 回复给谁的用户名颜色 */
     margin-right: 5px;
}

.replies-section {
    margin-top: 10px;
    padding-top: 10px; /* Add space above replies section */
    border-top: 1px dashed #eee; /* Optional: visual separator */
}

/* 子评论列表样式 */
.reply-list {
    margin-top: 10px;
}

.load-replies-button {
    background: none;
    border: none;
    color: #0077cc;
    cursor: pointer;
    font-size: 13px;
    margin-bottom: 10px; /* Space before replies list */
    display: block; /* Take full width */
    text-align: left; /* Align left */
    transition: text-decoration 0.2s ease;
}
.load-replies-button:hover {
    text-decoration: underline;
}


/* 评论分页样式 */
.comments-pagination {
    text-align: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.comments-pagination button {
    padding: 8px 15px;
    font-size: 15px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #fff;
    cursor: pointer;
    margin: 0 5px;
    transition: background-color 0.2s ease;
}

.comments-pagination button:hover:not(:disabled) {
    background-color: #f0f0f0;
}

.comments-pagination button:disabled {
    color: #ccc;
    cursor: not-allowed;
}

.comments-pagination span {
    margin: 0 10px;
    font-size: 15px;
    color: #555;
}

</style>
