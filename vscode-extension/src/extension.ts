// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "test" is now active!');

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json
	const disposable = vscode.commands.registerCommand('ai-buddy.helloWorld', async () => {
		copyTerminal();
	});

	context.subscriptions.push(disposable);
}

async function copyTerminal() {
		const terminal = vscode.window.activeTerminal;
		if (!terminal) {
			vscode.window.showErrorMessage('No active terminal found.');
			return;
		}

		// Select all in the terminal and copy to clipboard
		await vscode.commands.executeCommand('workbench.action.terminal.selectAll');
		await vscode.commands.executeCommand('workbench.action.terminal.copySelection');

		// Access clipboard content
		const selectedText = await vscode.env.clipboard.readText();

		// Clear the terminal selection
		await vscode.commands.executeCommand('workbench.action.terminal.clearSelection');

		// Display the captured text (or use it elsewhere in your extension)
		console.log('Captured Terminal Output:', selectedText);
		vscode.window.showInformationMessage(`Captured Terminal Output:\n${selectedText}`);
}

// This method is called when your extension is deactivated
export function deactivate() {}
