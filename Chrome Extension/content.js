document.addEventListener('mouseup', (event) => {
  let selectedText = window.getSelection().toString();

  if (selectedText !== '') {
    let button = document.createElement('button');
    button.innerText = 'Xác Minh';
    button.style.position = 'absolute';
    button.style.top = event.clientY + window.scrollY + 'px';
    button.style.left = event.clientX + window.scrollX + 'px';
    button.style.height = '30px';
    button.style.display = 'flex';
    button.style.justifyContent = 'center';
    button.style.alignItems = 'center';
    button.style.borderStyle = 'solid';
    button.style.borderRadius = '10px';
    button.style.backgroundColor = '#5f4dee';
    button.style.color = 'white';

    button.addEventListener('click', (event) => {
      chrome.runtime.sendMessage({
        action: 'highlight',
        text: selectedText,
      });
      button.remove();
    });

    setTimeout(() => {
      document.addEventListener('click', (event) => {
        if (!button.contains(event.target)) {
          button.remove();
        }
      });
    });

    document.body.appendChild(button);
  }
});
