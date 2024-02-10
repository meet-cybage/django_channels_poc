
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

    // Create the HTML string for the new li element
    var newLiHTML = `<li><div data-room-id=${resData.room_id} data-user-id=${resData.user} onclick="selectItem(this)"><span>${resData.username} (${resData.full_name})</span></div></li>`;

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
    debugger

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

function selectItem(clickedItem) {
    // Get the parent ul element
    // var parentList = clickedItem.parentNode;

    // Check if there's an element with the "selected" class
    var activeElement = document.querySelector('.selected');

    // If found, remove the "selected" class
    if (activeElement) {
        activeElement.classList.remove("selected");
    }

    // Add the "selected" class to the clicked li element
    clickedItem.classList.add("selected");
}
