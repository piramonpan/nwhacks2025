// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';

var provider: any = null;
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "test" is now active!');

	provider = new BuddyChat(context.extensionUri);
	context.subscriptions.push(vscode.window.registerWebviewViewProvider(BuddyChat.viewType, provider));

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json
	const disposable = vscode.commands.registerCommand('ai-buddy.helpTerminal', async () => {
		handleTerminalOutput();
	});

	context.subscriptions.push(disposable);
}

async function sendToAI(context: string, prompt: string) {
	// TODO: Send some data to the AI backend.
	console.log('(mock) AI received prompt \"' + prompt
				+ '\" with context:\n\'\'\'\n' + context + "\n\'\'\'");
}

async function handleTerminalOutput() {
	vscode.commands.executeCommand('workbench.view.extension.buddy');
	// Grabs output from the terminal and sends it to the AI
	let terminalOutput = await getLastNTerminalOutput(30);
	if (terminalOutput === null) {
		// Error already shown in getTerminalOutput(). Just return here.
		return;
	}
	let prompt = await vscode.window.showInputBox({prompt: "Question about terminal output", placeHolder: "Prompt to AI"});
	if (prompt) {
		sendToAI(terminalOutput, prompt);
	}
	provider.addUserMessage(prompt);
	
}

async function getLastNTerminalOutput(n: number): Promise<string | null> {
	let output = await getTerminalOutput();
	if (output === null) {
		// Error already shown in getTerminalOutput(). Just return here.
		return null
	}
	// Get at most n lines
	let truncatedOutput = output.split('\n').splice(-n).join('\n');
	return truncatedOutput;
}

async function getTerminalOutput(): Promise<string | null> {
	const terminal = vscode.window.activeTerminal;
	if (!terminal) {
		vscode.window.showErrorMessage('No terminal is currently active.');
		return null;
	}

	// Store original clipboard data to avoid clobbering too bad
	const originalClipboard = await vscode.env.clipboard.readText();

	// Logic to capture terminal output: https://github.com/mikekwright/vscode-terminal-capture
	
	// Select all in the terminal and copy to clipboard
	await vscode.commands.executeCommand('workbench.action.terminal.selectAll');
	await vscode.commands.executeCommand('workbench.action.terminal.copySelection');

	// Access clipboard content
	const selectedText = await vscode.env.clipboard.readText();

	// Clear the terminal selection
	await vscode.commands.executeCommand('workbench.action.terminal.clearSelection');

	// Restore clipboard to original text
	vscode.env.clipboard.writeText(originalClipboard);

	// Display the captured text (or use it elsewhere in your extension)
	return selectedText;
}

// This method is called when your extension is deactivated
export function deactivate() {}

class BuddyChat implements vscode.WebviewViewProvider {
	public static readonly viewType = 'buddy-chat';

	private _view?: vscode.WebviewView;
	
	constructor(private readonly _extensionUri: vscode.Uri){	}

	public resolveWebviewView(
		webviewView: vscode.WebviewView,
		_context: vscode.WebviewViewResolveContext,
		_token: vscode.CancellationToken,
	) {
		this._view = webviewView;

		webviewView.webview.options = {
			// Allow scripts in the webview
			enableScripts: true,

			localResourceRoots: [
				this._extensionUri
			]
		};

		//webviewView.webview.html = '<p>Hi!</p>';
		webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

		webviewView.webview.onDidReceiveMessage(data => {
			switch (data.type) {
				case 'colorSelected':
					{
						vscode.window.activeTextEditor?.insertSnippet(new vscode.SnippetString(`#${data.value}`));
						break;
		 			}
			}
		});		
	}

	public addAIMessage(message: string) {
		if (this._view) {
			this._view.show?.(true)
			this._view.webview.postMessage({ message : {user: "AI Buddy", chatMessage: message }})
		}
	}

	public addUserMessage(message: string) {
		if (this._view) {
			this._view.show?.(true)
			this._view.webview.postMessage({ message: { user: "User", chatMessage: message }})
		}
	}

	private _getHtmlForWebview(webview: vscode.Webview) {
		// Get the local path to main script run in the webview, then convert it to a uri we can use in the webview.
		// const jsMainUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'src', 'media', 'buddy.js'));
		const styleMainUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'src', 'media', 'buddy.css'));
		const logoUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'src', 'media', 'github-inverted-icon.png'));

		//const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'main.js'));
		const jsMainUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'src', 'media', 'buddy.js'));
		// Do the same for the stylesheet.
		//const styleResetUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'reset.css'));
		//const styleVSCodeUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'vscode.css'));
		//const styleMainUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'main.css'));
	
		return `<!DOCTYPE html>
			<html lang="en">

			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<link href="${styleMainUri}" rel="stylesheet">
				
				<title>AI Buddy</title>
			</head>

			<body>
				<div class="heading">
				</div>
				<div id="chat" class="chat">
					<ol class="message-list"></ol>

					<div class="message">
						<img class="pfp" src="${logoUri}" height="20px"/>
						<p class="text">Sample message</p>
					</div>
				</div>
				<form>
        			<label for="msg-input">You:</label>
					<input id="msg-input" type="text" placeholder="Ask a question..." />
					<button type="submit" onsubmit="console.log('A new message')">></button>
     			</form>
			<script src="${jsMainUri}"></script>
			</body>

			</html>`;
	}
}
