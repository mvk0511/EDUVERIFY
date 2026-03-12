// AI Chatbot Logic and UI for EduAssist AI
document.addEventListener("DOMContentLoaded", () => {
    // Inject the Chatbot HTML into the body
    const chatHTML = `
        <div id="eduAssistWrapper" class="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            <!-- Chat Window -->
            <div id="chatWindow" class="bg-white w-80 sm:w-96 rounded-2xl shadow-2xl border border-slate-200 overflow-hidden mb-4 transition-all duration-300 transform scale-0 origin-bottom-right opacity-0 hidden">
                <!-- Header -->
                <div class="bg-blue-600 p-4 text-white flex justify-between items-center shadow-md pb-4 pt-5">
                    <div class="flex items-center gap-3">
                        <div class="bg-white/20 p-2 rounded-full hidden sm:block">
                            <i class="fa-solid fa-robot"></i>
                        </div>
                        <div>
                            <h4 class="font-bold text-lg leading-tight">EduAssist AI</h4>
                            <span class="text-xs text-blue-200"><span class="inline-block w-2 h-2 bg-emerald-400 rounded-full mr-1 animate-pulse"></span>Online Assistant</span>
                        </div>
                    </div>
                    <button id="closeChat" class="text-white/80 hover:text-white transition-colors bg-blue-700/50 hover:bg-blue-700 w-8 h-8 rounded-full flex items-center justify-center"><i class="fa-solid fa-xmark"></i></button>
                </div>

                <!-- Chat Body -->
                <div id="chatMessages" class="px-4 py-5 h-80 overflow-y-auto bg-slate-50 space-y-4 text-sm scroll-smooth">
                    <!-- Default Greeting -->
                    <div class="flex gap-3">
                        <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shrink-0">
                            <i class="fa-solid fa-robot"></i>
                        </div>
                        <div class="bg-white border border-slate-200 p-3 rounded-2xl rounded-tl-none shadow-sm text-slate-700">
                            Hello! I am EduAssist AI. How can I help you today? You can ask me about deadlines, plagiarism rules, or assignment tracking!
                            <div class="text-[10px] text-slate-400 mt-1 text-right">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                        </div>
                    </div>
                </div>

                <!-- Input Area -->
                <div class="p-3 bg-white border-t border-slate-100 flex items-center gap-2">
                    <input type="text" id="chatInput" placeholder="Type your question..." class="flex-1 bg-slate-100 border-transparent focus:border-blue-500 focus:bg-white focus:ring-0 rounded-full py-2.5 px-4 text-sm outline-none transition-all">
                    <button id="sendChat" class="w-10 h-10 bg-blue-600 hover:bg-blue-700 text-white rounded-full flex items-center justify-center transition-colors shadow-sm"><i class="fa-solid fa-paper-plane text-sm"></i></button>
                </div>
            </div>

            <!-- Floating Toggle Button -->
            <button id="chatToggle" class="w-16 h-16 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-[0_8px_30px_rgb(37,99,235,0.4)] flex items-center justify-center text-2xl transition-all duration-300 hover:scale-110">
                <i class="fa-solid fa-comments"></i>
            </button>
        </div>
    `;

    document.getElementById('chatbot-container').innerHTML = chatHTML;

    // Elements
    const chatToggle = document.getElementById('chatToggle');
    const closeChat = document.getElementById('closeChat');
    const chatWindow = document.getElementById('chatWindow');
    const chatInput = document.getElementById('chatInput');
    const sendChat = document.getElementById('sendChat');
    const chatMessages = document.getElementById('chatMessages');

    // Toggle Chat visibility
    const toggleChat = () => {
        if (chatWindow.classList.contains('hidden')) {
            chatWindow.classList.remove('hidden');
            setTimeout(() => {
                chatWindow.classList.remove('scale-0', 'opacity-0');
                chatInput.focus();
            }, 10);
            chatToggle.innerHTML = `<i class="fa-solid fa-xmark"></i>`;
        } else {
            chatWindow.classList.add('scale-0', 'opacity-0');
            setTimeout(() => {
                chatWindow.classList.add('hidden');
            }, 300);
            chatToggle.innerHTML = `<i class="fa-solid fa-comments"></i>`;
        }
    };

    chatToggle.addEventListener('click', toggleChat);
    closeChat.addEventListener('click', toggleChat);

    // Typing Simulation Logic
    const addMessage = (text, isUser = false) => {
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex gap-3 ${isUser ? 'justify-end' : ''}`;

        const avatar = isUser ? '' : `<div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shrink-0"><i class="fa-solid fa-robot"></i></div>`;
        const styling = isUser ? 'bg-blue-600 text-white rounded-tr-none border-blue-700' : 'bg-white border-slate-200 text-slate-700 rounded-tl-none';

        msgDiv.innerHTML = `
            ${!isUser ? avatar : ''}
            <div class="${styling} min-w-[100px] border p-3 rounded-2xl shadow-sm max-w-[80%]">
                ${text}
                <div class="text-[10px] opacity-70 mt-1 ${isUser ? 'text-blue-100 text-left' : 'text-slate-400 text-right'}">${time}</div>
            </div>
            ${isUser ? `<img src="https://ui-avatars.com/api/?name=User&background=64748B&color=fff" class="w-8 h-8 rounded-full shrink-0">` : ''}
        `;

        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const generateBotResponse = async (msg) => {
        // Typing animation container
        const typingDiv = document.createElement('div');
        typingDiv.className = "flex gap-3 mt-2";
        typingDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-slate-200 text-slate-500 flex items-center justify-center shrink-0"><i class="fa-solid fa-ellipsis animate-pulse"></i></div>
            <div class="bg-slate-100 border border-slate-200 px-4 py-2 rounded-2xl rounded-tl-none shadow-sm text-slate-500 italic text-xs flex items-center">EduAssist is typing...</div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Current User for context
        const user = JSON.parse(localStorage.getItem('currentUser')) || { id: 0, role: 'student' };

        try {
            const response = await fetch('http://localhost:8000/api/chatbot/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.id || 0,
                    role: user.role || 'student',
                    message: msg
                })
            });

            const result = await response.json();
            chatMessages.removeChild(typingDiv);
            addMessage(result.reply || "I'm having trouble connecting to my brain right now.", false);
        } catch (error) {
            console.error('Chatbot API Error:', error);
            chatMessages.removeChild(typingDiv);
            addMessage("I'm sorry, I'm having trouble connecting to the server.", false);
        }
    };

    const handleSend = () => {
        const text = chatInput.value.trim();
        if (text) {
            addMessage(text, true);
            chatInput.value = '';
            generateBotResponse(text);
        }
    }

    sendChat.addEventListener('click', handleSend);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });
});
