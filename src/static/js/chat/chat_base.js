var messageInput = document.getElementById("message-input");

messageInput.addEventListener("keydown", function(event) {
    // Check if the pressed key is Enter (key code 13) and Shift key is not pressed
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // Prevent the default behavior (newline in textarea)
        sendMessage();
    }
});

function sendMessage() {
    var messageInput = document.getElementById('message-input');
    // var message = messageInput.value.trim();
    var message = messageInput.value.replace(/\n/g, '<br>').trim();
    
    if (message !== '') {
        var chatMessages = document.getElementById('chat-messages');
        var newMessage = document.createElement('div');
        newMessage.className = 'message-box';
        newMessage.innerHTML = '<span>User:</span><p>' + message + '</p>';
        chatMessages.appendChild(newMessage);

        // Clear the input field
        messageInput.value = '';

        // Scroll to the bottom of the chat messages
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}
