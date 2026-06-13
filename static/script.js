const chatScroll = document.getElementById('chat-scroll');
const chatMessages = document.getElementById('chat-messages');
const welcomeScreen = document.getElementById('welcome-screen');
const suggestionsEl = document.getElementById('suggestions');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const sidebarHistory = document.getElementById('sidebar-history');
const userSelect = document.getElementById('user-select');
const userAvatar = document.getElementById('user-avatar');

let chatHistory = [];
let currentChatId = null;
let currentUser = localStorage.getItem('serenity_current_user') || 'User 1';

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

// User state UI sync
function updateUserUI() {
    userSelect.value = currentUser;
    if (currentUser === 'User 1') {
        userAvatar.textContent = 'U1';
        userAvatar.style.backgroundColor = '#5436da';
    } else {
        userAvatar.textContent = 'U2';
        userAvatar.style.backgroundColor = '#da3654';
    }
}

// Local Storage helpers
function getChatsFromStorage() {
    const chatsJson = localStorage.getItem('serenity_chats');
    return chatsJson ? JSON.parse(chatsJson) : [];
}

function saveChatsToStorage(chats) {
    localStorage.setItem('serenity_chats', JSON.stringify(chats));
}

function renderSidebarHistory() {
    sidebarHistory.innerHTML = '';
    const chats = getChatsFromStorage();
    // Filter chats belonging to the active user (default older chats to User 1)
    const filteredChats = chats.filter(chat => (chat.user || 'User 1') === currentUser);
    
    filteredChats.slice().reverse().forEach(chat => {
        const item = document.createElement('div');
        item.className = 'history-item';
        if (chat.id === currentChatId) {
            item.classList.add('active');
        }
        item.dataset.id = chat.id;

        const titleSpan = document.createElement('span');
        titleSpan.textContent = chat.title;
        item.appendChild(titleSpan);

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'history-item-delete';
        deleteBtn.innerHTML = '&times;';
        deleteBtn.title = 'Delete chat';
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteChat(chat.id);
        });
        item.appendChild(deleteBtn);

        item.addEventListener('click', () => {
            loadChat(chat.id);
        });

        sidebarHistory.appendChild(item);
    });
}

function loadChat(chatId) {
    const chats = getChatsFromStorage();
    const chat = chats.find(c => c.id === chatId);
    if (!chat) return;

    currentChatId = chatId;
    chatHistory = chat.messages || [];

    chatMessages.innerHTML = '';
    if (welcomeScreen) welcomeScreen.style.display = 'none';
    if (suggestionsEl) suggestionsEl.style.display = 'none';

    chatHistory.forEach(msg => {
        chatMessages.appendChild(createMessageRow(msg.role, msg.content));
    });

    scrollToBottom();

    // Highlight active chat
    document.querySelectorAll('.history-item').forEach(el => {
        if (el.dataset.id === chatId) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });
}

function deleteChat(chatId) {
    let chats = getChatsFromStorage();
    chats = chats.filter(c => c.id !== chatId);
    saveChatsToStorage(chats);

    if (currentChatId === chatId) {
        startNewChat();
    } else {
        renderSidebarHistory();
    }
}

function startNewChat() {
    currentChatId = null;
    chatHistory = [];
    chatMessages.innerHTML = '';
    if (welcomeScreen) welcomeScreen.style.display = 'flex';
    if (suggestionsEl) suggestionsEl.style.display = 'flex';
    userInput.value = '';
    sendBtn.disabled = true;
    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
    renderSidebarHistory();
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Hide welcome & suggestions on first message
    if (welcomeScreen) welcomeScreen.style.display = 'none';
    if (suggestionsEl) suggestionsEl.style.display = 'none';

    // If starting a new session, create it in storage
    if (currentChatId === null) {
        const chatId = Date.now().toString();
        currentChatId = chatId;
        const chatTitle = text.length > 30 ? text.substring(0, 30) + '...' : text;
        const chats = getChatsFromStorage();
        chats.push({
            id: chatId,
            title: chatTitle,
            user: currentUser,
            messages: []
        });
        saveChatsToStorage(chats);
        renderSidebarHistory();
    }

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

        // Update localStorage
        const chats = getChatsFromStorage();
        const chatIndex = chats.findIndex(c => c.id === currentChatId);
        if (chatIndex !== -1) {
            chats[chatIndex].messages = chatHistory;
            saveChatsToStorage(chats);
        }

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

// User select listener
userSelect.addEventListener('change', (e) => {
    currentUser = e.target.value;
    localStorage.setItem('serenity_current_user', currentUser);
    updateUserUI();
    startNewChat();
});

// New chat button listener
document.getElementById('new-chat-btn').addEventListener('click', startNewChat);

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Initial load
updateUserUI();
renderSidebarHistory();
