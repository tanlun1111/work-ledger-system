/* ============================================================
   警情案件工作台账登记系统 - 工具函数
   ============================================================ */

/**
 * 日期时间格式化
 * @param {string|Date} date - 日期
 * @param {string} fmt - 格式字符串，默认 'YYYY-MM-DD HH:mm'
 * @returns {string}
 */
function formatDate(date, fmt) {
  if (!date) return '';
  fmt = fmt || 'YYYY-MM-DD HH:mm';
  var d = new Date(date);
  if (isNaN(d.getTime())) return '';
  var map = {
    'YYYY': d.getFullYear(),
    'MM': String(d.getMonth() + 1).padStart(2, '0'),
    'DD': String(d.getDate()).padStart(2, '0'),
    'HH': String(d.getHours()).padStart(2, '0'),
    'mm': String(d.getMinutes()).padStart(2, '0'),
    'ss': String(d.getSeconds()).padStart(2, '0')
  };
  return fmt.replace(/YYYY|MM|DD|HH|mm|ss/g, function(m) { return map[m]; });
}

/**
 * 将 YYYY-MM-DD HH:mm 转为 datetime-local input 的 value 格式
 * @param {string} str
 * @returns {string}
 */
function toDatetimeLocal(str) {
  if (!str) return '';
  return str.replace(' ', 'T');
}

/**
 * 将 datetime-local value 转为 YYYY-MM-DD HH:mm
 * @param {string} val
 * @returns {string}
 */
function fromDatetimeLocal(val) {
  if (!val) return '';
  return val.replace('T', ' ');
}

/**
 * 防抖
 * @param {Function} fn
 * @param {number} delay
 * @returns {Function}
 */
function debounce(fn, delay) {
  var timer = null;
  return function() {
    var context = this;
    var args = arguments;
    clearTimeout(timer);
    timer = setTimeout(function() { fn.apply(context, args); }, delay);
  };
}

/**
 * 文件大小格式化
 * @param {number} bytes
 * @returns {string}
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  var units = ['B', 'KB', 'MB', 'GB'];
  var i = Math.floor(Math.log(bytes) / Math.log(1024));
  return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i];
}

/**
 * HTML 转义
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * 从 URL query string 读取参数
 * @param {string} name
 * @returns {string|null}
 */
function getQueryParam(name) {
  var params = new URLSearchParams(window.location.search);
  return params.get(name);
}

/**
 * 更新 URL query string（不刷新页面）
 * @param {object} params - key/value 对象
 */
function updateQueryString(params) {
  var url = new URL(window.location);
  Object.keys(params).forEach(function(key) {
    var val = params[key];
    if (val === '' || val === null || val === undefined) {
      url.searchParams.delete(key);
    } else {
      url.searchParams.set(key, val);
    }
  });
  window.history.replaceState({}, '', url);
}

/**
 * 确认弹窗（使用 Bootstrap Modal）
 * @param {string} title
 * @param {string} message
 * @returns {Promise<boolean>}
 */
function confirmDialog(title, message) {
  return new Promise(function(resolve) {
    var existing = document.getElementById('confirmModal');
    if (existing) existing.remove();

    var html = '<div class="modal fade" id="confirmModal" tabindex="-1">' +
      '<div class="modal-dialog modal-sm modal-dialog-centered">' +
      '<div class="modal-content modal-delete">' +
      '<div class="modal-header"><h5 class="modal-title fs-6">' + escapeHtml(title) + '</h5>' +
      '<button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>' +
      '<div class="modal-body">' +
      '<div class="d-flex align-items-start gap-3">' +
      '<div class="warning-icon flex-shrink-0"><i class="bi bi-exclamation-triangle text-danger"></i></div>' +
      '<div class="flex-grow-1"><p class="mb-0 text-secondary">' + message + '</p></div>' +
      '</div></div>' +
      '<div class="modal-footer">' +
      '<button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">取消</button>' +
      '<button type="button" class="btn btn-danger btn-sm" id="confirmBtn">确认</button>' +
      '</div></div></div>';

    document.body.insertAdjacentHTML('beforeend', html);
    var modal = new bootstrap.Modal(document.getElementById('confirmModal'));
    modal.show();

    document.getElementById('confirmBtn').onclick = function() {
      modal.hide();
      resolve(true);
    };
    document.getElementById('confirmModal').addEventListener('hidden.bs.modal', function() {
      this.remove();
      resolve(false);
    });
  });
}

/**
 * 获取枚举缓存
 */
var enumCache = {
  _data: null,
  _expires: 0,

  get: async function() {
    if (this._data && Date.now() < this._expires) {
      return this._data;
    }
    try {
      var res = await api.get('/api/enums');
      this._data = res.data;
      this._expires = Date.now() + 5 * 60 * 1000;
      return this._data;
    } catch (e) {
      // 接口不可用时返回空
      return { info_source: [], case_category: [] };
    }
  },

  clear: function() {
    this._data = null;
    this._expires = 0;
  }
};

/**
 * 允许的图片类型
 */
var ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

/**
 * 最大图片大小 (10MB)
 */
var MAX_IMAGE_SIZE = 10 * 1024 * 1024;

/**
 * 最大图片数量
 */
var MAX_IMAGE_COUNT = 9;

/**
 * 校验文件类型和大小
 * @param {File} file
 * @returns {string|null} 错误消息或 null
 */
function validateImageFile(file) {
  if (ALLOWED_IMAGE_TYPES.indexOf(file.type) === -1) {
    return '不支持的文件类型：' + file.name;
  }
  if (file.size > MAX_IMAGE_SIZE) {
    return '文件大小超过 10MB：' + file.name;
  }
  return null;
}
