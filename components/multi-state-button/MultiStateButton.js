'use strict';

/**
 * MultiStateButton
 * A zero-dependency vanilla-JS component that cycles through a list of
 * states (emoji, text, or image URLs) every time the user clicks or taps it.
 *
 * @example
 * const btn = new MultiStateButton('#my-btn', {
 *   states: ['😐', '😊', '😂', '🤣'],
 *   onChange: (index, state) => console.log('Now at', index, state),
 * });
 */
class MultiStateButton {
  /**
   * @param {string|HTMLElement} element       CSS selector or DOM element to enhance.
   * @param {Object}  options
   * @param {Array}   options.states           Non-empty array of states.
   *                                           Each entry is either a plain string / emoji,
   *                                           or an object { content, label? } where
   *                                           `content` is the displayed value and `label`
   *                                           is used for aria-label.
   * @param {number}  [options.initialIndex=0] Index of the starting state.
   * @param {Function}[options.onChange]       Called after each transition:
   *                                           (newIndex: number, newState: any) => void
   */
  constructor(element, options = {}) {
    this._el = typeof element === 'string'
      ? document.querySelector(element)
      : element;

    if (!this._el) {
      throw new Error(`MultiStateButton: element not found — "${element}"`);
    }
    if (!Array.isArray(options.states) || options.states.length === 0) {
      throw new Error('MultiStateButton: options.states must be a non-empty array.');
    }

    this._states   = options.states;
    this._index    = options.initialIndex ?? 0;
    this._onChange = options.onChange     ?? null;

    this._init();
  }

  // ── Private ────────────────────────────────────────────────────────────────

  _init() {
    this._el.classList.add('msb');
    this._el.setAttribute('role', 'button');
    this._el.setAttribute('tabindex', '0');
    this._el.setAttribute('aria-live', 'polite');

    this._render();

    this._el.addEventListener('click', () => this._advance());
    this._el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this._advance();
      }
    });
  }

  _content(state) {
    if (typeof state === 'object' && state !== null) return state.content;
    return String(state);
  }

  _label(state) {
    if (typeof state === 'object' && state !== null) return state.label || state.content;
    return String(state);
  }

  _render() {
    const state = this._states[this._index];
    const content = this._content(state);

    // Support image URLs in addition to text / emoji
    if (/^https?:\/\/|^\/|^\.\//.test(content)) {
      this._el.innerHTML = `<img src="${content}" alt="${this._label(state)}" class="msb__img">`;
    } else {
      this._el.textContent = content;
    }

    this._el.setAttribute('aria-label', this._label(state));
    this._el.dataset.stateIndex = String(this._index);
  }

  _advance() {
    this._index = (this._index + 1) % this._states.length;

    // Restart pop animation
    this._el.classList.remove('msb--pop');
    void this._el.offsetWidth; // force reflow
    this._el.classList.add('msb--pop');
    this._el.addEventListener('animationend', () => {
      this._el.classList.remove('msb--pop');
    }, { once: true });

    this._render();

    if (this._onChange) {
      this._onChange(this._index, this._states[this._index]);
    }
  }

  // ── Public API ─────────────────────────────────────────────────────────────

  /** The index of the currently displayed state. */
  get currentIndex() { return this._index; }

  /** The currently displayed state value. */
  get currentState() { return this._states[this._index]; }

  /**
   * Programmatically jump to a state by index (does not fire onChange).
   * @param {number} index
   */
  setState(index) {
    if (index < 0 || index >= this._states.length) {
      throw new RangeError(`MultiStateButton.setState: index ${index} is out of range (0–${this._states.length - 1}).`);
    }
    this._index = index;
    this._render();
  }

  /** Reset to state index 0 (does not fire onChange). */
  reset() {
    this.setState(0);
  }
}
