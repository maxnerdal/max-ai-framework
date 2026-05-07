---
name: monitor-bemlo-tenders-0800
description: Monitor Bemlo tenders — weekdays 08:00
---

You are running an automated check of the Bemlo healthcare staffing platform for active tenders. Use Claude in Chrome to interact with the browser.

Navigate to: https://app.bemlo.com/vacancies/tenders

Use this JavaScript pattern whenever you need to type into a React input field (it triggers React's onChange properly):
```javascript
const input = document.querySelector('input[placeholder="PLACEHOLDER"]');
const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
setter.call(input, 'TEXT');
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));
```

---

PART 1 — Unspecialized Doctor tenders

Apply these filters in order before searching:

1. Click Filtrera:
   Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Filtrera').click()

2. Type 'Utbildning' into input[placeholder="Filtrera..."] using the React setter, then click the matching option in the listbox:
   document.querySelector('[role="listbox"]').querySelector('[role="option"]') and click it

3. Type 'Läkare' into input[placeholder="Filtrera..."] using the React setter, then click the matching Läkare option in the listbox

4. Press Escape to close the dropdown:
   document.activeElement.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))

5. Click the "alla specialiseringar" chip in the filter bar:
   Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'alla specialiseringar').click()

6. Type 'ingen specialisering' into input[placeholder="Filtrera..."] using the React setter, then click the matching option

7. Press Escape to close

Verify the filter bar shows "läkare | ingen specialisering" before continuing.

Now search for each department one at a time using input[placeholder="Sök..."]:
- "Hälsocentralen Sollefteå"
- "Hälsocentralen Kramfors"

Clear the Sök... box between searches (set value to '').

---

PART 2 — Leg nurse tenders

Remove all active filters: find the SVG X button near the filter chips (button with no text whose SVG path contains "M6 18L18 6") and click it:
```javascript
const clearBtn = Array.from(document.querySelectorAll('button')).find(b => {
  const path = b.querySelector('path');
  return path && path.getAttribute('d') && path.getAttribute('d').includes('M6 18L18 6');
});
if (clearBtn) clearBtn.click();
```
Then verify no filter chips remain.

Search input[placeholder="Sök..."] one at a time with NO filters active:
- "Stroke och rehabiliteringsavdelning Örnsköldsvik"
- "Hematologi och Njuravdelning Örnsköldsvik"
- "Närvårdsavdelningen i Uppsala"

Clear the Sök... box between searches.

---

After each search, check results with:
```javascript
const links = Array.from(document.querySelectorAll('a[href^="/vacancies/"]'));
const results = links.map(l => l.innerText.replace(/\s+/g, ' ').trim()).filter(t => t.length > 10);
const countMatch = document.body.innerText.match(/Visar\s+(\d+)\s+resultat/i);
({ count: countMatch ? countMatch[1] : '0', results })
```

---

WORKSHIFT LOOKUP

For every tender that returns 1 or more results, fetch its workshifts. For each tender link found:

1. Extract the vacancy UUID from the link href (the 36-character UUID after `/vacancies/`):
```javascript
const links = Array.from(document.querySelectorAll('a[href^="/vacancies/"]'));
const uuids = [...new Set(links.map(l => l.href.match(/\/vacancies\/([0-9a-f-]{36})/)?.[1]).filter(Boolean))];
uuids
```

2. For each UUID, query the Bemlo GraphQL API (uses your existing browser session/cookies):
```javascript
const q = `{ vacancy(id: "UUID_HERE") { tender { shifts { shift { date startTime endTime } } } } }`;
fetch('https://api.bemlo.ai/graphql', {
  method: 'POST', credentials: 'include',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: q})
}).then(r => r.json()).then(d => { window.__shifts = d; });
```

3. After ~2 seconds, read and format the result:
```javascript
const shifts = (window.__shifts?.data?.vacancy?.tender?.shifts || []).map(s => s.shift);
shifts.sort((a, b) => a.date.localeCompare(b.date) || a.startTime.localeCompare(b.startTime));
shifts.map(s => {
  const [, m, d] = s.date.split('-');
  const startHour = parseInt(s.startTime.split(':')[0]);
  const pass = startHour >= 6 && startHour < 13 ? 'Dagpass'
             : startHour >= 13 && startHour < 21 ? 'Kvällspass'
             : 'Nattpass';
  return `${parseInt(d)}/${parseInt(m)} ${pass}`;
}).join('\n')
```

---

REPORTING RULES:
- If any search returns 1 or more results: report the full tender details (ID, department, profession, specialization, period, deadline, hours, price SEK/hr, status), then list the workshifts in this format:
  12/5 Dagpass
  13/5 Kvällspass
  21/5 Kvällspass
- If all searches return 0 results: report "No new tenders found"
- IMPORTANT: 0 results with filters active is correct and expected for Part 1 — never remove filters to get results