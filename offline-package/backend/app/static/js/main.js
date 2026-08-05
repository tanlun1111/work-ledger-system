const api = {
  async request(url, options = {}, timeout = 30000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);

    const headers = {
      'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || '',
      ...options.headers
    };

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const res = await fetch(url, { ...options, headers, signal: controller.signal });
      clearTimeout(timer);
      const json = await res.json();
      if (json.code === 401) {
        window.location.href = '/login?expired=1';
        throw new ApiError(json.code, json.message);
      }
      if (json.code !== 200) {
        throw new ApiError(json.code, json.message);
      }
      return json;
    } catch (err) {
      clearTimeout(timer);
      if (err.name === 'AbortError') throw new ApiError(0, '请求超时，请稍后重试');
      if (err instanceof ApiError) throw err;
      throw new ApiError(0, '网络异常，请检查网络连接');
    }
  },

  get(url, params = {}) {
    const qs = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== null && v !== undefined && v !== '') qs.append(k, v);
    }
    const qsStr = qs.toString();
    return this.request(url + (qsStr ? '?' + qsStr : ''));
  },

  post(url, data) {
    return this.request(url, { method: 'POST', body: data });
  },

  patch(url, data) {
    return this.request(url, { method: 'PATCH', body: data });
  },

  delete(url) {
    return this.request(url, { method: 'DELETE' });
  },

  async postFormData(url, formData, fieldName = 'files') {
    const fd = formData instanceof FormData ? formData : (() => {
      const f = new FormData();
      f.append(fieldName, formData);
      return f;
    })();
    return this.request(url, { method: 'POST', body: fd });
  }
};

async function changePassword() {
  const oldPw = document.getElementById('oldPw').value;
  const newPw = document.getElementById('newPw').value;
  const confirmPw = document.getElementById('confirmPw').value;

  if (!oldPw || !newPw) { Toast.show('请填写旧密码和新密码', 'warning'); return; }
  if (newPw.length < 6) { Toast.show('新密码最少 6 位', 'warning'); return; }
  if (newPw !== confirmPw) { Toast.show('两次输入的新密码不一致', 'warning'); return; }

  const btn = document.getElementById('btnConfirmPw');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>修改中...';

  try {
    await api.post('/api/change-password', JSON.stringify({ old_password: oldPw, new_password: newPw }));
    Toast.show('密码修改成功');
    document.getElementById('oldPw').value = '';
    document.getElementById('newPw').value = '';
    document.getElementById('confirmPw').value = '';
    bootstrap.Modal.getInstance(document.getElementById('changePasswordModal')).hide();
  } catch (e) {
    Toast.show(e.message || '修改失败', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '确认修改';
  }
}

class ApiError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
    this.name = 'ApiError';
  }
}

const Toast = {
  show(message, type = 'success', duration = 3000) {
    const container = document.getElementById('globalToastContainer');
    if (!container) return;
    const bgMap = { success: 'bg-success text-white', error: 'bg-danger text-white', warning: 'bg-warning text-dark', info: 'bg-info text-dark' };
    const iconMap = { success: 'bi-check-circle-fill', error: 'bi-exclamation-triangle-fill', warning: 'bi-exclamation-circle-fill', info: 'bi-info-circle-fill' };
    const bgClass = bgMap[type] || 'bg-success text-white';
    const icon = iconMap[type] || 'bi-check-circle-fill';

    const wrapper = document.createElement('div');
    wrapper.innerHTML = `<div class="toast align-items-center ${bgClass} border-0" role="alert">
      <div class="d-flex">
        <div class="toast-body"><i class="bi ${icon} me-2"></i>${message}</div>
        <button class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div></div>`;
    const el = wrapper.firstElementChild;
    container.appendChild(el);
    const toast = new bootstrap.Toast(el, { delay: duration });
    toast.show();
    el.addEventListener('hidden.bs.toast', () => el.remove());
  }
};
