// Executes the real page script with DOM/fetch stand-ins; this is not a browser test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

class Element {
  constructor() {
    this.children = [];
    this.value = '';
    this.disabled = false;
    this.listeners = {};
    this.text = '';
  }
  set textContent(value) { this.text = String(value); this.children = []; }
  get textContent() { return this.text + this.children.map(child => child.textContent).join(''); }
  set innerHTML(value) { throw new Error('Render untrusted output with textContent'); }
  replaceChildren(...children) { this.text = ''; this.children = children; }
  append(...children) { this.children.push(...children); }
  addEventListener(type, listener) { this.listeners[type] = listener; }
}

async function main() {
  const page = fs.readFileSync(path.join(__dirname, '../app/page.html'), 'utf8');
  const script = page.match(/<script>([\s\S]*?)<\/script>/)[1];
  const elements = Object.fromEntries([
    'announcement-form', 'announcement', 'posted-date', 'submit-button',
    'status', 'draft-fields', 'missing-fields', 'uncertain-fields'
  ].map(id => [id, new Element()]));
  const announcement = '  <script>untrusted announcement</script>\nWorkshop  ';
  elements.announcement.value = announcement;
  elements['posted-date'].value = '2026-10-20';
  let respond;
  let reject;
  let posted;
  vm.runInNewContext(script, {
    document: {
      getElementById: id => {
        assert.ok(elements[id], `Unexpected element ${id}`);
        return elements[id];
      },
      createElement: () => new Element()
    },
    fetch: (url, options) => {
      assert.equal(url, '/draft');
      assert.equal(options.method, 'POST');
      assert.equal(options.headers['Content-Type'], 'application/json');
      posted = JSON.parse(options.body);
      return new Promise((resolve, rejectRequest) => { respond = resolve; reject = rejectRequest; });
    }
  });
  const submit = () => elements['announcement-form'].listeners.submit({ preventDefault() {} });
  const assertPreserved = () => {
    assert.equal(elements.announcement.value, announcement);
    assert.equal(elements['posted-date'].value, '2026-10-20');
    assert.equal(elements['submit-button'].disabled, false);
  };
  const draft = {
    title: '<img src=x onerror=alert(1)>', description: 'Join the workshop.',
    date: '2026-11-03', time: '18:00', location: 'Holmes 244', sig: 'SWITCH',
    kind: 'Workshop', missing_fields: ['time'], uncertain_fields: ['date'],
    source_quotes: {
      title: 'Intro to Git', description: 'Join us', date: 'Nov 3', time: '6 PM',
      location: 'Holmes 244', sig: 'SWITCH', kind: 'workshop'
    }
  };
  let pending = submit();
  assert.equal(elements['submit-button'].disabled, true);
  assert.deepEqual(posted, { announcement_text: announcement, posted_date: '2026-10-20' });
  respond({ ok: true, status: 200, json: async () => draft });
  await pending;
  assert.equal(elements['draft-fields'].children.length, 7);
  for (const key of ['title', 'description', 'date', 'time', 'kind', 'location', 'sig']) {
    assert.ok(elements['draft-fields'].textContent.includes(draft[key]));
  }
  for (const field of elements['draft-fields'].children) {
    assert.equal(field.children[3].disabled, true);
  }
  for (const quote of Object.values(draft.source_quotes)) {
    assert.ok(elements['draft-fields'].textContent.includes('Source: ' + quote));
  }
  assert.ok(elements['missing-fields'].textContent.includes('time'));
  assert.ok(elements['uncertain-fields'].textContent.includes('date'));
  assert.match(elements.status.textContent, /review/i);
  assertPreserved();
  console.log('PASS success: fields, quotes, flags, literal untrusted text, values, and restored submit');

  const failures = [
    [422, { detail: [{ loc: ['body', 'posted_date'], msg: 'Invalid date' }] }, /announcement|posted date/i],
    [503, { detail: 'sentinel-provider-detail' }, /configur|unavailable/i],
    [502, { detail: 'sentinel-provider-detail' }, /try again|retry/i]
  ];
  for (const [status, body, message] of failures) {
    elements['draft-fields'].textContent = 'STALE DRAFT';
    elements['missing-fields'].textContent = 'STALE FLAGS';
    elements['uncertain-fields'].textContent = 'STALE FLAGS';
    pending = submit();
    assert.ok(!elements['draft-fields'].textContent.includes('STALE'));
    assert.ok(!elements['missing-fields'].textContent.includes('STALE'));
    assert.ok(!elements['uncertain-fields'].textContent.includes('STALE'));
    assert.equal(elements['submit-button'].disabled, true);
    respond({ ok: false, status, json: async () => body });
    await pending;
    assert.match(elements.status.textContent, message);
    assert.ok(!elements.status.textContent.includes('[object Object]'));
    assert.ok(!elements.status.textContent.includes('sentinel-provider-detail'));
    assert.ok(!elements['draft-fields'].textContent.includes(draft.title));
    assertPreserved();
    console.log(`PASS ${status}: stale output cleared before fetch, readable safe error, values and submit restored`);
  }
  pending = submit();
  reject(new Error('sentinel-provider-detail'));
  await pending;
  assert.match(elements.status.textContent, /server|connection|network/i);
  assert.ok(!elements.status.textContent.includes('sentinel-provider-detail'));
  assertPreserved();
  console.log('PASS network failure: readable safe error, values and submit restored');
}

main().catch(error => { console.error(error); process.exitCode = 1; });
