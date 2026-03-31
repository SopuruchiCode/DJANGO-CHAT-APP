async function get_username() {
    try{
        const response = await fetch(`http://${window.location.host}/info/username-reveal/`);
        const data = await response.json();
        sessionStorage.setItem("username", data["username"]);
    }
    catch(err){
        console.log(err);
    }
}

async function activate() {
    const profileSearchElem = document.querySelector(".search");
    const accListElem = document.querySelector(".chat-list");

    const websocket = new WebSocket(`wss://${window.location.host}/ws/chat-search/`);
    // const websocket = new WebSocket(`ws://${window.location.host}/ws/chat-search/`);
    websocket.addEventListener("open", (event) => {
        console.log("Websocket established");
        get_username();       
    })

    websocket.addEventListener("message", (event) => {
        data = JSON.parse(event.data);

        if(data.type === "conversation_starter" && data.outcome === "conversation_created"){
            url = new URL(`https://${window.location.host}/`);
            url.searchParams.set("convo_partner", data["convo_partner"]);
            window.location.href = url.toString();
        }
        else{
            accListElem.innerHTML = "";

            if(data.length === 0){
                accListElem.innerHTML = "No results found";
            }
            for (const account of data){
                
                accListElem.innerHTML += `
                    <div class="chat-result">
                            <div>
                                <img src=${account.profile_pic_path}>
                                <span>
                                    ${account.username}
                                </span>
                            </div>
                            <div class="btn-div">
                                <button class="msgBtn" id="${account.username.replaceAll("@","")}">
                                    Message
                                </button>
                            </div>
                        </div>
                `;
                if(account.username.replaceAll("@","") === sessionStorage.getItem("username")){
                    document.querySelector(".btn-div").innerHTML = ``;
                }
            }
            msgBtns = document.querySelectorAll(".msgBtn");
            for (const btn of msgBtns){
                btn.addEventListener("click", (event) => {
                    websocket.send(JSON.stringify({
                        "type": "conversation_starter",
                        "username": `${event.target.id}`
                    }))
                })
            }
        }
    })

    websocket.addEventListener("close", (event) => {
        
    })

    profileSearchElem.addEventListener("input", (event) => {
        if (event.target.value.trim() !== ""){
            const data = {
                "search_query": event.target.value
            }
            websocket.send(JSON.stringify(data));
        }else{
            accListElem.innerHTML = "No results found";
        }
    })
    
}

activate();