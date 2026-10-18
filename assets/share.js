(() => {
  'use strict';
  const dialog = document.createElement('dialog');
  dialog.className = 'share-dialog';
  dialog.setAttribute('aria-labelledby', 'share-heading');
  dialog.innerHTML = '<h2 id="share-heading">分享程式</h2><p class="share-name"></p><label for="share-link">公開連結</label><input id="share-link" type="url" readonly><p class="share-help" role="status" aria-live="polite">複製連結後，可貼到 LINE、訊息、Email 或其他平台。</p><div class="share-actions"><button type="button" class="share-copy">複製連結</button><button type="button" class="share-close">關閉</button></div>';
  document.body.append(dialog);
  const input = dialog.querySelector('input');
  const help = dialog.querySelector('.share-help');
  const copy = dialog.querySelector('.share-copy');
  const close = dialog.querySelector('.share-close');
  let trigger;

  function showLink(title, url, button) {
    trigger = button;
    dialog.querySelector('.share-name').textContent = title;
    input.value = url;
    help.textContent = '複製連結後，可貼到 LINE、訊息、Email 或其他平台。';
    dialog.showModal();
    input.focus();
    input.select();
  }

  copy.addEventListener('click', async () => {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(input.value);
      help.textContent = '已複製連結，可以貼上分享了！';
    } catch {
      help.textContent = '瀏覽器無法自動複製。請長按連結，或按 Ctrl+C（Mac：⌘C）手動複製。';
      input.focus();
      input.select();
    }
  });
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => trigger?.focus());

  document.addEventListener('click', async event => {
    const button = event.target.closest('button[data-share-url]');
    if (!button || button.disabled) return;
    const pageUrl = window.location.href;
    const url = new URL(button.dataset.shareUrl || pageUrl, pageUrl);
    url.search = '';
    url.hash = '';
    const title = button.dataset.shareTitle || document.title;
    button.disabled = true;
    try {
      if (navigator.share) {
        await navigator.share({ title, url: url.href });
      } else {
        showLink(title, url.href, button);
      }
    } catch (error) {
      if (error.name !== 'AbortError') showLink(title, url.href, button);
    } finally {
      button.disabled = false;
    }
  });
})();
