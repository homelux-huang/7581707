const { test } = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../assets/share.js'), 'utf8');

function setup(navigator = {}, shareUrl = 'https://homelux-huang.github.io/7581707/%E6%B8%AC%E8%A9%A6%20%23.HTML?answer=private#score', currentUrl = 'https://seven581707.onrender.com/Gemini%20Canvas%E6%9C%83%E8%A8%88%E6%A8%A1%E6%93%AC%E8%80%83.html?answers=private#score') {
  const nodes = new Map();
  const element = () => ({
    events: {}, value: '', textContent: '', opened: false,
    setAttribute() {}, focus() { this.focused = true; },
    select() { this.selected = true; },
    addEventListener(name, action) { this.events[name] = action; },
    querySelector(selector) {
      if (!nodes.has(selector)) nodes.set(selector, element());
      return nodes.get(selector);
    },
    showModal() { this.opened = true; },
    close() { this.opened = false; this.events.close(); },
  });
  const dialog = element();
  const button = element();
  button.dataset = {
    shareUrl,
    shareTitle: '測試程式',
  };
  let handler;
  const document = {
    title: 'Page title', body: { append() {} },
    createElement: () => dialog,
    addEventListener: (name, action) => { handler = action; },
  };
  vm.runInNewContext(source, { document, navigator, URL, window: { location: { href: currentUrl } } });
  return {
    dialog, button, nodes,
    click: () => handler({ target: { closest: () => button } }),
  };
}

test('native share sends only the public title and URL, without answer state', async () => {
  let data;
  const app = setup({ share: async value => { data = value; } });
  await app.click();
  assert.equal(data.title, '測試程式');
  assert.equal(data.url, 'https://homelux-huang.github.io/7581707/%E6%B8%AC%E8%A9%A6%20%23.HTML');
  assert.equal(Object.keys(data).length, 2);
  assert.equal(app.dialog.opened, false);
  assert.equal(app.button.disabled, false);
});

test('canceling the system share sheet does not open another dialog', async () => {
  const app = setup({ share: async () => { throw { name: 'AbortError' }; } });
  await app.click();
  assert.equal(app.dialog.opened, false);
  assert.equal(app.button.disabled, false);
});

test('unsupported native share provides a selectable public link', async () => {
  const app = setup();
  await app.click();
  assert.equal(app.dialog.opened, true);
  assert.equal(app.nodes.get('input').selected, true);
  assert.equal(app.nodes.get('input').value.includes('?'), false);
});

test('blocked native share falls back to the link dialog', async () => {
  const app = setup({ share: async () => { throw { name: 'NotAllowedError' }; } });
  await app.click();
  assert.equal(app.dialog.opened, true);
});

test('clipboard success is shown only after the write succeeds', async () => {
  let copied;
  const app = setup({ clipboard: { writeText: async value => { copied = value; } } });
  await app.click();
  await app.nodes.get('.share-copy').events.click();
  assert.equal(copied, app.nodes.get('input').value);
  assert.match(app.nodes.get('.share-help').textContent, /已複製/);
});

test('denied or unavailable clipboard offers manual copy', async () => {
  for (const navigator of [{}, { clipboard: { writeText: async () => { throw new Error('Denied'); } } }]) {
    const app = setup(navigator);
    await app.click();
    await app.nodes.get('.share-copy').events.click();
    assert.match(app.nodes.get('.share-help').textContent, /手動複製/);
    assert.equal(app.nodes.get('input').selected, true);
  }
});

test('closing the link dialog returns focus to its share button', async () => {
  const app = setup();
  await app.click();
  app.nodes.get('.share-close').events.click();
  assert.equal(app.dialog.opened, false);
  assert.equal(app.button.focused, true);
});

test('current tool page shares the active Render URL without private state', async () => {
  let data;
  const app = setup({ share: async value => { data = value; } }, '');
  await app.click();
  assert.equal(data.url, 'https://seven581707.onrender.com/Gemini%20Canvas%E6%9C%83%E8%A8%88%E6%A8%A1%E6%93%AC%E8%80%83.html');
});

test('relative share URLs preserve the host and subpath on GitHub Pages', async () => {
  let data;
  const app = setup({ share: async value => { data = value; } }, './gemini%20canvas%E6%9C%83%E8%A8%88%E7%B5%B1%E6%B8%AC%E7%A8%8B%E5%BC%8F.html?answer=private#score', 'https://homelux-huang.github.io/7581707/');
  await app.click();
  assert.equal(data.url, 'https://homelux-huang.github.io/7581707/gemini%20canvas%E6%9C%83%E8%A8%88%E7%B5%B1%E6%B8%AC%E7%A8%8B%E5%BC%8F.html');
});

test('homepage uses the same resolved URL for open and share', () => {
  const home = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
  assert.match(home, /share\.dataset\.shareUrl = link\.href;/);
});
