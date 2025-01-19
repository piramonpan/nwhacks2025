// This script will be run within the webview itself
// It cannot access the main VS Code APIs directly.
(function () {
	const vscode = acquireVsCodeApi();

	const oldState = vscode.getState() || { messages: [] };

	let messages = oldState.messages;

	updateMessageList(messages);

	// Handle messages sent from the extension to the webview
	window.addEventListener('message', event => {
		const message = event.data.message; // The json data that the extension sent
		addMessage(message);
	});

	function updateMessageList(messages) {
		const ol = document.querySelector('.message-list');
		ol.textContent = ''; // TODO: What is this for?
		for (const message of messages) {
			const li = document.createElement('input');
			li.className = 'message';
			li.type = 'text';
			li.value = message.user + ": " + message.message;
			// li.user = message.user;
			// li.message = message.message;
			ol.appendChild(li);
		}

		// Update the saved state
		vscode.setState({ messages: messages });
	}

	function addMessage(message) {
		messages.push({ user: message.user, message: message.message});
		updateMessageList(messages);
	}

}());



