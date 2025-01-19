// This script will be run within the webview itself
// It cannot access the main VS Code APIs directly.
(function () {
	const vscode = acquireVsCodeApi();

	const oldState =  { chatMessages: [] };

	let chatMessages = oldState.chatMessages;

	updateMessageList(chatMessages);

	// Handle messages sent from the extension to the webview
	window.addEventListener('message', event => {
		const chatMessage = event.data.message; // The json data that the extension sent
		addMessage(chatMessage);
	});

	document.querySelector('.send').addEventListener('click', () => {
		//console.log("clicked!");
		const chatMessage = { user: "You", chatMessage: document.getElementById("msg-input").value }
		addMessage(chatMessage);
		document.getElementById("msg-input").value = '';
		//console.log("added message from user");
		vscode.postMessage({ message: chatMessage.chatMessage })
	});

	function updateMessageList(chatMessages) {
		const ol = document.querySelector('.message-list');
		ol.textContent = '';
		for (const chatMessage of chatMessages) {
			const li = document.createElement('li');
			if (chatMessage.user == 'You'){
				li.className = 'chatMessage human';
			} else {
				li.className = 'chatMessage ai';
			}
			// li.type = 'text';
			//li.textContent = chatMessage.user + ": " + chatMessage.chatMessage;
			li.innerHTML = `${chatMessage.user}: ${chatMessage.chatMessage.replace(/\n/g, '<br>')}`;
			// li.user = message.user;
			// li.message = message.message;
			ol.appendChild(li);
		}

		// Scroll to the bottom of the chat
		scrollToBottom();

		// Update the saved state
		vscode.setState({ chatMessages: chatMessages });
	}

	function scrollToBottom() {
		element = document.getElementById("chat");
		setTimeout(() => {
			element.scrollTop = element.scrollHeight;
		}, 0); // Ensure the DOM has time to update
	}

	function appendToLastMessage(chatMessageChunk) {
		chatMessages[chatMessages.length - 1].chatMessage += chatMessageChunk;
	}

	function addMessage(chatMessage) {
		if (chatMessage.user == "-1") {
			appendToLastMessage(chatMessage.chatMessage);
			updateMessageList(chatMessages);
		} else {
			chatMessages.push(chatMessage);
			updateMessageList(chatMessages);
		}
	}
}());



