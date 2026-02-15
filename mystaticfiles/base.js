// experimental
// before websocket usage
// testing

function getCSRFToken(){
    return document.getElementsByName("csrfmiddlewaretoken")[0].value;
}

async function getChatData(username){
    let response = await fetch(`/get-chat-data/${username}/`);
    let data = await response.json();

    const profile_pic_img = document.querySelector(".chat-profile-intro .chat-profile-pic img");
    const chat_name = document.querySelector(".actual-chat-name");
    const p_username = document.querySelector(".username");
    const mainChatTextDiv = document.querySelector(".main-chat-texts");

    profile_pic_img.src = data["profile_pic_url"];
    chat_name.innerHTML = `${data["first_name"]} ${data["last_name"]}`;
    p_username.innerHTML = `@${username}`
    
    const message_date = data["message_date"];
    mainChatTextDiv.innerHTML = ``;

    for (const [date, messages] of Object.entries(message_date)){
        mainChatTextDiv.innerHTML += `
                    <div class="chat-day-con">
                        <div class="chat-day">
                            ${date}
                        </div>
                    </div>
        `;

        for(const message of messages){
            if (message.sender !== `${username}`){
                mainChatTextDiv.innerHTML += 
                `
                    <div class="user-text-bubble-con">
                        <div class="user-text-bubble bubble">
                            <!-- <div class="txt-bbl-profile-pic">
                                <img>
                            </div>

                            <div class="txt-bbl-username">
                                <p> @johndoe</p>
                            </div> -->

                            <div class="actual-chat-text">
                                <pre class="chat-message">${message["text"]}</pre>
                            </div>

                            <div class="chat-text-meta">
                                <div class="main-chat-read-receipt">
                                    ??
                                </div>

                                <div class="main-chat-time-stamp">
                                    ${message["time_created"]}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }else{
                mainChatTextDiv.innerHTML += 
                `
                    <div class="partner-text-bubble-con">
                        <div class="partner-text-bubble bubble">
                            <!-- <div class="txt-bbl-profile-pic">
                                <img>
                            </div>

                            <div class="txt-bbl-username">
                                <p> @johndoe</p>
                            </div> -->

                            <div class="actual-chat-text">
                                <pre class="chat-message">${message["text"]}</pre>
                            </div>

                            <div class="chat-text-meta">
                                <div class="main-chat-read-receipt">
                                    ??
                                </div>

                                <div class="main-chat-time-stamp">
                                    ${message["time_created"]}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
        }

    }
    document.querySelector(".main-chat-texts").scrollTo(
        {
            top: document.querySelector(".main-chat-texts").scrollHeight,
            left:0, 
            behavior:"instant"
        })
    // const user_text_bubble_con = document.createElement("div");
    // user_text_bubble_con.classList.add("user-text-bubble-con");

    // const user_text_bubble = document.createElement("div");
    // user_text_bubble.classList.add("user-text-bubble", "bubble");

    // const actual_chat_text = document.createElement("div");
    // actual_chat_text.classList.add("actual-chat-text");

    // const chat_message = document.createElement("pre");
    // chat_message.classList.add("chat-message");

    // const chat_text_meta = document.createElement("div");
    // chat_text_meta.classList.add("chat-text-meta");

    // const main_chat_read_receipt =document.createElement("div");
    // main_chat_read_receipt.classList.add("main-chat-read-receipt");

    // const main_chat_time_stamp = document.createElement("div");
    // main_chat_time_stamp.classList.add("main-chat-time-stamp");
}

const chats = document.querySelectorAll(".chat-div");
const activeChatRecord = {
    "last-active" : null,
}

function activateChat(id){
    const elem = document.querySelector(`#${id}`);
    const lastActiveID = activeChatRecord["last-active"];

    if(lastActiveID){
        const lastActiveElem = document.querySelector(`#${lastActiveID}`);
        lastActiveElem.style.backgroundColor = "transparent";
        leaveChat(lastActiveID)
    }
    elem.style.backgroundColor = "#115111";
    activeChatRecord["last-active"] = id;
}


const url = "ws://" + window.location.host + `/ws/chat/`;
const websocket = new WebSocket(url);

websocket.addEventListener("open", (e) => {
    console.log("Socket connection established")
})

websocket.addEventListener("message", (event) => {
    data = JSON.parse(event.data);
    if (data.type === "message"){
        const mainChatTextDiv = document.querySelector(".main-chat-texts");
        if (data["recipient"] === activeChatRecord["last-active"] || data["sender"] === activeChatRecord["last-active"]){
            if (data["sender"] !== activeChatRecord["last-active"]){
                mainChatTextDiv.innerHTML += 
                `
                    <div class="user-text-bubble-con">
                        <div class="user-text-bubble bubble">
                            <!-- <div class="txt-bbl-profile-pic">
                                <img>
                            </div>

                            <div class="txt-bbl-username">
                                <p> @johndoe</p>
                            </div> -->

                            <div class="actual-chat-text">
                                <pre class="chat-message">${data["message_text"]}</pre>
                            </div>

                            <div class="chat-text-meta">
                                <div class="main-chat-read-receipt">
                                    ??
                                </div>

                                <div class="main-chat-time-stamp">
                                    ${data["time_created"]}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }else{
                mainChatTextDiv.innerHTML += 
                `
                    <div class="partner-text-bubble-con">
                        <div class="partner-text-bubble bubble">
                            <!-- <div class="txt-bbl-profile-pic">
                                <img>
                            </div>

                            <div class="txt-bbl-username">
                                <p> @johndoe</p>
                            </div> -->

                            <div class="actual-chat-text">
                                <pre class="chat-message">${data["message_text"]}</pre>
                            </div>

                            <div class="chat-text-meta">
                                <div class="main-chat-read-receipt">
                                    ??
                                </div>

                                <div class="main-chat-time-stamp">
                                    ${data["time_created"]}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
            document.querySelector(".main-chat-texts").scrollTo(
                {
                    top: document.querySelector(".main-chat-texts").scrollHeight,
                    left:0, 
                    behavior:"smooth"
                })
        }
    }
})

websocket.addEventListener("close", (e) => {
    console.log("Socket connection disconnected")
})

function joinChat(friend_username){
    websocket.send(JSON.stringify({
        "data_type": "join_chat",
        "friend_username": friend_username
    }))
}

function leaveChat(friend_username){
    websocket.send(JSON.stringify({
        "data_type": "leave_chat",
        "friend_username": friend_username
    }))
}
const formElem = document.querySelector("#message-form");
const msg_text_input = document.getElementById("msg_text_input");

formElem.addEventListener("submit", async (event) => {
    event.preventDefault();

    const data = {
        "data_type": "msg_txt",
        "message_text": msg_text_input.value,
        "recipient": activeChatRecord["last-active"] || ""
    }
    websocket.send(JSON.stringify(data));
    msg_text_input.value = "";

})
document.querySelector(".scroll-down").addEventListener("click", (event) => {
    document.querySelector(".main-chat-texts").scrollTo(
        {
            top: document.querySelector(".main-chat-texts").scrollHeight,
            left:0, 
            behavior:"smooth"
        })
})

for (let element of chats) {
    element.addEventListener("click", () => {
        getChatData(element.id);
        activateChat(element.id);
        joinChat(element.id);
        msg_text_input.value = "";
    });
}



group_chats = document.querySelector(".group-div");


function joinGroupChat(id){
    websocket.send(JSON.stringify({
        "data_type": "join_group_chat",
        "id": id
    }))
}

function leaveGroupChat(id){
    websocket.send(JSON.stringify({
        "data_type": "leave_group_chat",
        "id": id
    }))
}

//function sendGroupMessage(id)
const ClickEvent = new Event("click")

const searchParamString = window.location.search;
if (searchParamString){
    const searchParam = new URLSearchParams(searchParamString);
    const chatUsername = searchParam.get("convo_partner");
    if (chatUsername){
        const chatElement = document.querySelector(`#${chatUsername}`);
        if (chatElement){
            chatElement.dispatchEvent(ClickEvent);
        }
    }
}
const chat_search = document.querySelector(".chat-search");



//     const form_data = new FormData(formElem);

//     if (msg_text_input.value.trim() === ""){
//         console.log("Empty string");
//         return null;                                //  to prevent sending empty strings
//     }
//     const data = await fetch("http://" + window.location.host + "/", {
//         method: "POST",
//         headers: {
//             "X-CSRFToken": getCSRFToken(),
//         },
//         body: form_data
//     }

// )

