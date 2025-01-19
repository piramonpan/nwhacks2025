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

	function updateMessageList(chatMessages) {
		const ol = document.querySelector('.message-list');
		ol.textContent = ''; // TODO: What is this for?
		for (const chatMessage of chatMessages) {
			const li = document.createElement('input');
			li.className = 'chatMessage';
			li.type = 'text';
			li.value = chatMessage.user + ": " + chatMessage.chatMessage;
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



