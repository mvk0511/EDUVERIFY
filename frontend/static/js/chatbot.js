// AI Chatbot Link Redirect
document.addEventListener("DOMContentLoaded", () => {
    // Inject just the floating button into the body
    const chatHTML = `
        <div id="eduAssistWrapper" class="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            <!-- Floating Toggle Button -->
            <button id="chatToggle" class="w-16 h-16 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-[0_8px_30px_rgb(37,99,235,0.4)] flex items-center justify-center text-2xl transition-all duration-300 hover:scale-110" title="Open Abby Calm Companion Chatbot">
                <i class="fa-solid fa-comments"></i>
            </button>
        </div>
    `;

    document.getElementById('chatbot-container').innerHTML = chatHTML;

    // Elements
    const chatToggle = document.getElementById('chatToggle');

    // Toggle Chat visibility - redirects to provided link
    const toggleChat = () => {
        window.open('https://abby-calm-companion.lovable.app/', '_blank');
    };

    chatToggle.addEventListener('click', toggleChat);
});
