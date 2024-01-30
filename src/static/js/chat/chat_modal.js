
async function fetchData(url) {
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
            normalUserTags += `<li onclick="selectItem(this)">${item.username}</li>`;
            groupUserTags += `<li><input type="checkbox" onclick="groupUserSelectedCount(this)" id="${item.username}"> <label for="${item.username}">${item.username}</label></li>`;
        });

        // Log the updated values
        // console.log(normalUserTags, "/////////////////////////////");
        // console.log(groupUserTags, "/////////////////////////////");

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
    let [normalUserTags, groupUserTags] = await fetchData(url)
    
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
        
                <input type="text" class="group-name-input" placeholder="Enter group name...">
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

function createGroup() {
    // Retrieve selected users
    var selectedUsers = document.querySelectorAll('#users-popup-list-create-group input:checked');

    // Display the count of selected users
    var selectedUsersCount = document.getElementById('selected-users-count');
    selectedUsersCount.innerText = selectedUsers.length;

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
    var parentList = clickedItem.parentNode;

    // Check if there's an element with the "selected" class
    var activeElement = parentList.querySelector('.selected');

    // If found, remove the "selected" class
    if (activeElement) {
        activeElement.classList.remove("selected");
    }

    // Add the "selected" class to the clicked li element
    clickedItem.classList.add("selected");

    // Handle selected users in the Create Group tab
    if (parentList.id === 'selected-popup-users') {
        var selectedUsersContainer = document.getElementById('selected-popup-users');
        var userChip = document.createElement('div');
        userChip.className = 'user-chip';
        userChip.innerText = clickedItem.innerText;

        // Check if the user is already selected
        if (!selectedUsersContainer.querySelector(`.user-chip[data-user="${clickedItem.innerText}"]`)) {
            userChip.setAttribute('data-user', clickedItem.innerText);
            selectedUsersContainer.appendChild(userChip);
        }
    }
}
