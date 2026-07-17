/* ============================================================
   警情案件工作台账登记系统 - API 封装
   ============================================================ */

var API_BASE = '';

var api = {
  /**
   * 通用请求
   * @param {string} url
   * @param {object} options - fetch 选项
   * @param {number} timeout - 超时毫秒，默认 30000
   * @returns {Promise<{code: number, message: string, data: any}>}
   */
  request: async function(url, options, timeout) {
    options = options || {};
    timeout = timeout || 30000;

    var controller = new AbortController();
    var timer = setTimeout(function() { controller.abort(); }, timeout);

    var headers = {
      'X-CSRFToken': (document.querySelector('meta[name="csrf-token"]') || {}).content || '',
    };
    if (options.headers) {
      Object.keys(options.headers).forEach(function(k) {
        headers[k] = options.headers[k];
      });
    }

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      var res = await fetch(API_BASE + url, {
        method: options.method || 'GET',
        headers: headers,
        body: options.body,
        signal: controller.signal
      });
      clearTimeout(timer);

      var json = await res.json();
      if (json.code !== 200) {
        throw { code: json.code, message: json.message };
      }
      return json;
    } catch (err) {
      clearTimeout(timer);
      if (err.name === 'AbortError') {
        throw { code: 0, message: '请求超时，请稍后重试' };
      }
      if (err.code !== undefined) throw err;
      throw { code: 0, message: '网络异常，请检查网络连接' };
    }
  },

  get: function(url, params) {
    params = params || {};
    var qs = new URLSearchParams(params).toString();
    return this.request(url + (qs ? '?' + qs : ''));
  },

  post: function(url, data) {
    return this.request(url, { method: 'POST', body: JSON.stringify(data) });
  },

  patch: function(url, data) {
    return this.request(url, { method: 'PATCH', body: JSON.stringify(data) });
  },

  delete: function(url) {
    return this.request(url, { method: 'DELETE' });
  },

  postFormData: function(url, file, fieldName) {
    fieldName = fieldName || 'files';
    var formData = new FormData();
    formData.append(fieldName, file);
    return this.request(url, { method: 'POST', body: formData });
  }
};
