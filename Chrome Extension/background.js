chrome.runtime.onMessage.addListener((message) => {
  if (message.action === 'highlight') {
    chrome.windows.create({
      url: `./popup/popup.html?text=${message.text}`,
      type: 'panel',
    });
  }
});
