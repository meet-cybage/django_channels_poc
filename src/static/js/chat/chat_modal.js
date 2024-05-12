
var chatSocket = null;
var roomName;

async function fetchUsersData(url) {
    var normalUserTags = "";
    var groupUserTags = "";

    try {
        const response = await fetch(url, { method: "GET" });

        if (!response.ok) {
            throw new Error("Network response was not ok");
        }

        const data = await response.json();

        // Now you can iterate over the resolved data
        data.forEach((item) => {
            if (item.full_name != " ") {
                normalUserTags += `<li data-userId=${item.id} onclick="createUserChatRoom(this)">${item.username} (${item.full_name})</li>`;
                groupUserTags += `<li><input type="checkbox" data-userId=${item.id} onclick="groupUserSelectedCount(this)" id="${item.username}"> <label for="${item.username}">${item.username} (${item.full_name})</label></li>`;
            }
            else{
                normalUserTags += `<li data-userId=${item.id} onclick="createUserChatRoom(this)">${item.username}</li>`;
                groupUserTags += `<li><input type="checkbox" data-userId=${item.id} onclick="groupUserSelectedCount(this)" id="${item.username}"> <label for="${item.username}">${item.username}</label></li>`;
            }
            
        });

        // Perform any other actions that depend on the resolved data here
        return [normalUserTags, groupUserTags]
    } catch (error) {
        console.error("Error:", error);
        // Handle error scenarios here
    }
}


async function openModal(ele) {
    var modal = document.getElementById("myModal");
    modal.style.display = "flex";
    var url = ele.getAttribute("data-user-url")
    let [normalUserTags, groupUserTags] = await fetchUsersData(url)
    
    modal_tags = `
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
        

            <div class="tab-container">
                <div class="tab" onclick="changeTab(0)">Search Users</div>
                <div class="tab" onclick="changeTab(1)">Create Group</div>
            </div>
        

            <div id="tab-search-users" class="tab-content active">
                <input type="text" class="search-bar-enhanced" placeholder="Search users...">
                <div class="users-popup-list" id="users-popup-list-search">
                    <ul>
                        ${normalUserTags}
                    </ul>
                </div>
            </div>
        

            <div id="tab-create-group" class="tab-content">
                <input type="text" class="search-bar-enhanced" placeholder="Search users to add to the group...">
                <div class="selected-popup-users" id="selected-popup-users">
                    <span id="selected-users-count">0</span> users selected
                </div>
        
                <input type="text" class="group-name-input" id="groupName" placeholder="Enter group name...">
                <button id="create-button" onclick="createGroup()">Create</button>
        
        
                <div class="users-popup-list" id="users-popup-list-create-group">
                    <ul>
                        ${groupUserTags}   
                    </ul>
                </div>
            </div>
        </div>
    `
    modal.innerHTML = modal_tags
}

function closeModal() {
    var modal = document.getElementById("myModal");
    modal.style.display = "none";
    modal.innerHTML = ""
}

/* This is extra function */
function selectItem(clickedItem) {
    // Get the parent ul element
    // var parentList = clickedItem.parentNode;

    // Check if there's an element with the "selected" class
    var activeElement = document.querySelector('.selected');
    console.log(activeElement, "***************************")

    // If found, remove the "selected" class
    if (activeElement) {
        activeElement.classList.remove("selected");
    }

    // Add the "selected" class to the clicked li element
    clickedItem.classList.add("selected");
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function createChatRoom(data){
    try {
        const url = "/chat/create/room"
        
        const dataString = JSON.stringify(data);
        // const csrfToken = await generateCSRFToken(dataString)
        const csrfToken = getCookie('csrftoken');
        const response = await fetch(url, {
             method: "POST",
             headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
             },
             body: JSON.stringify(data)
            }
        );

        if (!response.ok) {
            throw new Error("Network response was not ok");
        }

        return await response.json();
    }
    catch(error){

    }
}

function addNewUserElement(listType, resData){
    // Find the li element with the text content "# Users"
    var usersLi = document.querySelector(`[data-type="${listType}"]`);

    if (listType == "Users"){
        // Create the HTML string for the new li element
        var newLiHTML = `<li><div data-room-id=${resData.room_id} data-user-id=${resData.user} onclick="selectItem(this)"><span>${resData.username} (${resData.full_name})</span></div></li>`;
    }
    else{
        // Create the HTML string for the new li element
    var newLiHTML = `<li><div data-room-id=${resData.room_id} data-group-id=${resData.group_id} onclick="selectItem(this)"><span>${resData.group_name}</span></div></li>`;
    }
    

    // Insert the new li element after the # Users li element
    usersLi.insertAdjacentHTML('afterend', newLiHTML);
    var newUser = document.querySelector(`[data-room-id="${resData.room_id}"]`)
    selectItem(newUser)
}

async function createUserChatRoom(ele) {
    user = ele.getAttribute("data-userId")
    const data = {
        "users": user,
        "room_type": "Users"
    }
    const resData = await createChatRoom(data)
    closeModal();

    addNewUserElement("Users", resData);

}


function changeTab(tabIndex) {
    var tabContents = document.querySelectorAll('.tab-content');
    var tabs = document.querySelectorAll('.tab');

    // Hide all tab contents
    tabContents.forEach(tab => tab.classList.remove('active'));

    // Show the selected tab content
    document.getElementById(`tab-search-users`).classList.toggle("active", tabIndex === 0);
    document.getElementById(`tab-create-group`).classList.toggle("active", tabIndex === 1);

    // Activate the selected tab
    tabs.forEach(tab => tab.classList.remove('active'));
    tabs[tabIndex].classList.add('active');
}

async function createGroup() {
    // Retrieve selected users
    var selectedUsers = document.querySelectorAll('#users-popup-list-create-group input:checked');
    var groupName = document.getElementById('groupName').value

    // Display the count of selected users
    var selectedUsersCount = document.getElementById('selected-users-count');
    selectedUsersCount.innerText = selectedUsers.length;

    let userIds= []
    selectedUsers.forEach(user => userIds.push(user.getAttribute("data-userId")))

    const data = {
        "users": userIds,
        "room_type": "Groups",
        "group_name": groupName
    }

    const resData = await createChatRoom(data)
    addNewUserElement("Groups", resData);
    closeModal();

    // addNewUserElement("Groups", resData);

    // Display the selected users in the console (you can modify this logic)
    selectedUsers.forEach(user => console.log(user.nextElementSibling.innerText));
}

function groupUserSelectedCount(checkBox) {
    var totalUsers = document.getElementById('selected-users-count')
    var usersCount = parseInt(totalUsers.innerText)

    if (checkBox.checked){
        usersCount = usersCount + 1
        totalUsers.innerText = usersCount
    }
    else{
        usersCount = usersCount - 1
        totalUsers.innerText = usersCount
    }
}

var chatMessages = document.getElementById('chat-messages');

function getScrollChatMessages(){
    var activeElement = document.querySelector('.selected');
    const data = {
        "room_id": activeElement.getAttribute("data-room-id")
    }

    const groupId = activeElement.getAttribute("data-group-id")
    const roomUserId = activeElement.getAttribute("data-user-id")

    if (groupId !== null) {
        data["group_id"] = groupId;
    }

    if (roomUserId !== null) {
        data["room_user_id"] = roomUserId;
    }

    const start = $('#startInput').val()

    if (start !== "null") {
        data['start'] = start
        $.ajax({
            url: "/chat/messages",
            type: 'GET',
            contentType: 'application/json',
            data: data,
            success: function(responseData) {

                responseData.chat_messages.forEach((item) => {

                    if (item.sender_full_name == " "){
                        var user = `${item.sender_username}`
                    }
                    else{
                        var user = `${item.sender_username} (${item.sender_full_name})`
                    }
                    var newHtml = `
                        <div class="message-box" data-room-id="${item.chat_room_id}">
                            <span>${user}:</span>
                            <p>${item.message}</p>
                        </div>
                    `

                    $("#startInput").after(newHtml)

                })

                if (responseData.chat_messages.length === 10) {
                    $('#startInput').val(responseData.end);
                }
                else{
                    $('#startInput').val("null");
                }            

            }
        })
    }

}


// function handleScroll(event) {
//     if ((event.type === 'scroll' && chatMessages.scrollTop === 0) ||
//         (event.type === 'wheel' && event.deltaY < 0 && chatMessages.scrollTop === 0)) {
//         console.log("Scroll at the top");
//         getScrollChatMessages();
//     }
// }

// Define a debounce function
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        timeoutId = setTimeout(() => {
            func.apply(this, args);
            timeoutId = null;
        }, delay);
    };
}

function handleScroll(event) {
    if (event.deltaY < 0 || chatMessages.scrollTop === 0) {
        console.log("Scroll at the top");
        getScrollChatMessages();
    }
}

// Add a debounced event listener for both scroll and wheel events
const debouncedHandleScroll = debounce(handleScroll, 300); // Adjust the delay as needed

chatMessages.addEventListener('scroll', debouncedHandleScroll);
chatMessages.addEventListener('wheel', debouncedHandleScroll);


async function getChatMessages(chatMessages, data){

    $.ajax({
        url: "/chat/messages",
        type: 'GET',
        contentType: 'application/json',
        data: data,
        success: function(data) {

            data.chat_messages.forEach((item) => {

                if (item.sender_full_name == " "){
                    var user = `${item.sender_username}`
                }
                else{
                    var user = `${item.sender_username} (${item.sender_full_name})`
                }
                var newHtml = `
                    <div class="message-box" data-room-id="${item.chat_room_id}">
                        <span>${user}:</span>
                        <p>${item.message}</p>
                    </div>
                `

                chatMessages.insertAdjacentHTML("beforeend", newHtml)
            })

            // $("#startInput").after("<h1>hello</h1>")
            // $("#startInput").after("<h1>hello1</h1>")
            $('#startInput').val(data.end);

        }
    })

}

async function selectItem(clickedItem) {
    // Get the parent ul element
    // var parentList = clickedItem.parentNode;

    // Check if there's an element with the "selected" class
    var activeElement = document.querySelector('.selected');

    // If found, remove the "selected" class
    if (activeElement) {
        if (chatSocket){
            chatSocket.close()
        }
        activeElement.classList.remove("selected");
    }

    // Add the "selected" class to the clicked li element
    clickedItem.classList.add("selected");

    roomName = `room_${clickedItem.getAttribute("data-room-id")}`
    chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/chat/'
        + roomName
        + '/'
    );
    
    chatSocket.onmessage = function (event) {
        // Handle incoming messages here, or pass them to the global handler
        var data = JSON.parse(event.data)
        var chatMessages = document.getElementById('chat-messages');
        var messageInput = document.getElementById('message-input');
        var newMessage = document.createElement('div');
        newMessage.className = 'message-box';
        newMessage.setAttribute('data-room-id', data.room_id);
        newMessage.innerHTML = '<span>User:</span><p>' + data.message + '</p>';
        chatMessages.appendChild(newMessage);

        // Clear the input field
        messageInput.value = '';

        // Scroll to the bottom of the chat messages
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };
    var spanText = clickedItem.querySelector('span').innerText;

    var existingSpan = document.querySelector('.nav-right-span');
    var newElement = `<div id="userDiv" style="color: grey; padding-left=250px"><span style="font-size=25px"> ${spanText}</span></div>`
    var imgElement = existingSpan.querySelector('img');
    var existingNewElement = existingSpan.querySelector('#userDiv');

    if (existingNewElement) {
        existingNewElement.remove()
    }
    imgElement.insertAdjacentHTML('afterend', newElement);
    
    const data = {
        "room_id": clickedItem.getAttribute("data-room-id")
    }

    const groupId = clickedItem.getAttribute("data-group-id")
    const roomUserId = clickedItem.getAttribute("data-user-id")

    var chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';

    var inputHtml = `
        <input type="hidden" id="startInput" value="0">
    `
    data["start"] = 0
    chatMessages.insertAdjacentHTML("beforeend", inputHtml)

    if (groupId !== null) {
        data["group_id"] = groupId;
    }

    if (roomUserId !== null) {
        data["room_user_id"] = roomUserId;
    }
    
    await getChatMessages(chatMessages, data);
    // chatMessages.scrollTop = chatMessages.scrollHeight;
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100); 


}
