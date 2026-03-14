const button = document.querySelector<HTMLButtonElement>('#triggerBtn');

if (!button) {
  throw new Error('Missing #triggerBtn');
}

button.addEventListener('click', () => {
  window.api.openPanelFromBubble();
});
