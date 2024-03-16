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

$(document).ready(function() {

    var ele = document.getElementById("usersAndGroups")
    var url = ele.getAttribute("data-url")

    $.ajax({                       
        url: url,
        success: function (data) { 
            var userDetailsTags = ""
            var groupDetailsTags = ""

            data.users_data.forEach(ele => {
                if (ele.room_user_full_name != " ") {
                    userDetailsTags += `<li><div data-room-id=${ele.chat_room_id} data-user-id=${ele.room_user_id} onclick="selectItem(this)"><span>${ele.room_username}(${ele.room_user_full_name})</span></div></li>`
                }
                else{
                    userDetailsTags += `<li><div data-room-id=${ele.chat_room_id} data-user-id=${ele.room_user_id} onclick="selectItem(this)"><span>${ele.room_username}</span></div></li>`
                }
            });

            data.groups_data.forEach(ele => {
                groupDetailsTags += `<li><div data-room-id=${ele.chat_room_id} data-group-id=${ele.group_id} onclick="selectItem(this)"><span>${ele.group_name}</span></div></li>`
            });
            
            var html = `
                <ul class="users">
                <li data-type="Users"><h3># Users</h3></li>
                ${userDetailsTags}
                <li data-type="Groups"><h3># Groups</h3></li>
                ${groupDetailsTags}
                </ul>
            `
            $("#usersAndGroups").html(html);
        }
    });
});