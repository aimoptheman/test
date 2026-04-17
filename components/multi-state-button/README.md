# MultiStateButton

A zero-dependency, accessible vanilla-JS component that cycles through a list of states (emoji, text, or image URLs) every time the user clicks or taps it.  Works out of the box on desktop and mobile.

---

## Installation

Copy the two files into your project and link them in your HTML:

```html
<link rel="stylesheet" href="MultiStateButton.css">
<script src="MultiStateButton.js"></script>
```

No build step, no npm install required.

---

## Quick start

```html
<!-- 1. Add a placeholder element -->
<span id="mood"></span>

<!-- 2. Link the assets -->
<link rel="stylesheet" href="MultiStateButton.css">
<script src="MultiStateButton.js"></script>

<!-- 3. Initialise -->
<script>
  const btn = new MultiStateButton('#mood', {
    states: ['😐', '😊', '😂', '🤩'],
  });
</script>
```

Click or tap the button to cycle through the states.

---

## Options

| Option | Type | Default | Description |
|---|---|---|---|
| `states` | `Array` | *(required)* | Non-empty array of states. Each entry can be a string/emoji **or** an object `{ content, label? }` (see below). |
| `initialIndex` | `number` | `0` | Index of the state shown on first render. |
| `onChange` | `function` | `null` | Called after every transition: `(newIndex, newState) => void`. |

### State formats

```js
// Plain string or emoji
states: ['🌑', '🌒', '🌓', '🌔', '🌕']

// Object with optional accessible label
states: [
  { content: '🔴', label: 'Recording stopped' },
  { content: '🟢', label: 'Recording started' },
]

// Absolute or relative image URL
states: [
  { content: 'https://example.com/off.png', label: 'Off' },
  { content: 'https://example.com/on.png',  label: 'On'  },
]
```

---

## API

```js
const btn = new MultiStateButton(element, options);
```

| Member | Type | Description |
|---|---|---|
| `btn.currentIndex` | `number` | Index of the current state *(read-only)*. |
| `btn.currentState` | `any` | Value of the current state *(read-only)*. |
| `btn.setState(n)` | `void` | Jump to state `n` without firing `onChange`. |
| `btn.reset()` | `void` | Jump back to index 0 without firing `onChange`. |

---

## Theming

Override any CSS custom property on `:root` or on a parent element:

```css
#my-button {
  --msb-size:        4rem;
  --msb-font-size:   2rem;
  --msb-border:      2px solid #6c63ff;
  --msb-bg:          #f0eeff;
  --msb-bg-hover:    #e2dcff;
  --msb-focus-color: #6c63ff;
}
```

---

## Live demo

Open [`../../demo/multi-state-button.html`](../../demo/multi-state-button.html) in your browser.
