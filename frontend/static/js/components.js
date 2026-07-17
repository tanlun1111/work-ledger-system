/* ============================================================
   警情案件工作台账登记系统 - 全局 UI 组件
   ============================================================ */

/**
 * Toast 消息
 */
var Toast = {
  show: function(message, type, duration) {
    type = type || 'success';
    duration = duration || 3000;

    var container = document.getElementById('globalToastContainer');
    if (!container) return;

    var bgClass = {
      success: 'bg-success text-white',
      error: 'bg-danger text-white',
      warning: 'bg-warning',
      info: 'bg-info'
    }[type] || 'bg-success text-white';

    var icon = {
      success: 'bi-check-circle-fill',
      error: 'bi-exclamation-triangle-fill',
      warning: 'bi-exclamation-circle-fill',
      info: 'bi-info-circle-fill'
    }[type] || 'bi-check-circle-fill';

    var html = '<div class="toast align-items-center ' + bgClass + ' border-0" role="alert">' +
      '<div class="d-flex">' +
      '<div class="toast-body"><i class="bi ' + icon + ' me-2"></i>' + escapeHtml(message) + '</div>' +
      '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
      '</div></div>';

    var el = document.createElement('div');
    el.innerHTML = html;
    container.appendChild(el.firstElementChild);
    var toastEl = container.lastElementChild;
    var toast = new bootstrap.Toast(toastEl, { delay: duration });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', function() { toastEl.remove(); });
  }
};

/**
 * 图片查看器
 */
function openImageViewer(imageUrl, imageList, currentIndex) {
  // 移除已存在的查看器
  var existing = document.getElementById('imageViewerOverlay');
  if (existing) existing.remove();

  var currentIdx = currentIndex || 0;
  var images = imageList || [{ url: imageUrl }];

  var overlay = document.createElement('div');
  overlay.id = 'imageViewerOverlay';
  overlay.className = 'image-viewer-overlay';

  overlay.innerHTML =
    '<button class="close-btn" onclick="document.getElementById(\'imageViewerOverlay\').remove()">' +
    '<i class="bi bi-x-lg"></i></button>' +
    '<img src="' + images[currentIdx].url + '" alt="" id="viewerImg">';

  // 支持键盘导航
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) overlay.remove();
  });
  document.addEventListener('keydown', function esc(e) {
    if (e.key === 'Escape') overlay.remove();
  });

  document.body.appendChild(overlay);
}

/**
 * 处理 API 错误并显示 Toast
 * @param {object} err - {code, message}
 * @param {string} fallbackMsg - 兜底消息
 */
function handleApiError(err, fallbackMsg) {
  fallbackMsg = fallbackMsg || '操作失败，请稍后重试';
  var msg = err.message || fallbackMsg;
  Toast.show(msg, 'error');
}
