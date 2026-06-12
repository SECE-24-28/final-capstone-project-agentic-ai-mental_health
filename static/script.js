const chatScroll = document.getElementById('chat-scroll');
const chatMessages = document.getElementById('chat-messages');
const welcomeScreen = document.getElementById('welcome-screen');
const suggestionsEl = document.getElementById('suggestions');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const sidebarHistory = document.getElementById('sidebar-history');

let chatHistory = [];
let chatCount = 0;

// Auto-resize textarea
userInput.addEventListener('input', () => {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 200) + 'px';
    sendBtn.disabled = !userInput.value.trim();
});

function scrollToBottom() {
    chatScroll.scrollTop = chatScroll.scrollHeight;
}

function createMessageRow(role, content) {
    const row = document.createElement('div');
    row.className = 'message-row';

    const avatar = document.createElement('div');
    avatar.className = `msg-avatar ${role === 'assistant' ? 'bot' : 'user'}`;
    avatar.textContent = role === 'assistant' ? 'S' : 'U';

    const body = document.createElement('div');
    body.className = 'msg-body';

    const name = document.createElement('div');
    name.className = 'msg-name';
    name.textContent = role === 'assistant' ? 'Serenity AI' : 'You';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'msg-content';
    contentDiv.innerHTML = role === 'assistant' ? marked.parse(content) : escapeHtml(content);

    body.appendChild(name);
    body.appendChild(contentDiv);
    row.appendChild(avatar);
    row.appendChild(body);
    return row;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showTyping() {
    const row = document.createElement('div');
    row.className = 'typing-row';
    row.id = 'typing';

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar bot';
    avatar.textContent = 'S';

    const body = document.createElement('div');
    body.className = 'msg-body';
    const name = document.createElement('div');
    name.className = 'msg-name';
    name.textContent = 'Serenity AI';
    const dots = document.createElement('div');
    dots.className = 'typing-dots';
    dots.innerHTML = '<span></span><span></span><span></span>';

    body.appendChild(name);
    body.appendChild(dots);
    row.appendChild(avatar);
    row.appendChild(body);
    chatMessages.appendChild(row);
    scrollToBottom();
}

function hideTyping() {
    const el = document.getElementById('typing');
    if (el) el.remove();
}

function addToHistory(text) {
    chatCount++;
    const item = document.createElement('div');
    item.className = 'history-item';
    item.textContent = text.length > 30 ? text.substring(0, 30) + '...' : text;
    sidebarHistory.prepend(item);
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Hide welcome & suggestions on first message
    if (welcomeScreen) welcomeScreen.style.display = 'none';
    if (suggestionsEl) suggestionsEl.style.display = 'none';

    // Add to sidebar history
    if (chatHistory.length === 0) addToHistory(text);

    chatMessages.appendChild(createMessageRow('user', text));
    userInput.value = '';
    userInput.style.height = 'auto';
    sendBtn.disabled = true;
    scrollToBottom();

    showTyping();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, history: chatHistory })
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Server error');
        }

        const data = await res.json();
        hideTyping();
        chatMessages.appendChild(createMessageRow('assistant', data.response));

        chatHistory.push({ role: 'user', content: text });
        chatHistory.push({ role: 'assistant', content: data.response });

    } catch (err) {
        hideTyping();
        chatMessages.appendChild(createMessageRow('assistant',
            `⚠️ *Error: ${err.message}*`));
    }

    scrollToBottom();
    userInput.focus();
}

function useSuggestion(btn) {
    // Get just the text, not the SVG
    const text = btn.textContent.trim();
    userInput.value = text;
    sendBtn.disabled = false;
    sendMessage();
}

// New chat
document.getElementById('new-chat-btn').addEventListener('click', () => {
    chatHistory = [];
    chatMessages.innerHTML = '';
    if (welcomeScreen) welcomeScreen.style.display = 'flex';
    if (suggestionsEl) suggestionsEl.style.display = 'flex';
    userInput.value = '';
    sendBtn.disabled = true;
});

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
