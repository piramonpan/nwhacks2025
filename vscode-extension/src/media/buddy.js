// This script will be run within the webview itself
// It cannot access the main VS Code APIs directly.
(function () {
	const vscode = acquireVsCodeApi();

	const oldState =  vscode.getState() || { chatMessages: [] };

	let chatMessages = oldState.chatMessages;

	updateMessageList(chatMessages);

	// Handle messages sent from the extension to the webview
	window.addEventListener('message', event => {
		const chatMessage = event.data.message; // The json data that the extension sent
		addMessage(chatMessage);
	});

	document.querySelector('.send').addEventListener('click', () => {
		//console.log("clicked!");
		const chatMessage = {user: "You", chatMessage: document.getElementById("msg-input").value}
        addMessage(chatMessage);
		document.getElementById("msg-input").value = '';
		//console.log("added message from user");
		vscode.postMessage({ message: 'hello Z!' })
    });

	function updateMessageList(chatMessages) {
		const ol = document.querySelector('.message-list');
		ol.textContent = '';
		for (const chatMessage of chatMessages) {
			const li = document.createElement('li');
			li.className = 'chatMessage';
			// li.type = 'text';
			li.textContent = chatMessage.user + ": " + chatMessage.chatMessage;
			// li.user = message.user;
			// li.message = message.message;
			ol.appendChild(li);
		}

		// Update the saved state
		vscode.setState({ chatMessages: chatMessages });
	}

	function addMessage(chatMessage) {
		chatMessages.push(chatMessage);
		updateMessageList(chatMessages);
	}
}());



