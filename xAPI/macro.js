// A simple call to a pre defined address based on a room control event

const xapi = require('xapi');

function dial(uri) {
	
	console.log('dial', uri); // Log that we have called the dial function to the macro leg
	xapi.command('dial', { Number: uri }); // Xcommand Dial with the passed URI from the parameter field

}

function listenToGui() {
	
	// If the user interfaction event triggers we will listed to it and perform the following code
	// All the informarion about the event is passed in the "event" object
	xapi.event.on('UserInterface Extensions Panel Clicked', (event) => {

		// If the event equals "clicked" and the id is equal to call_john, we will execute the code within
		if (event.PanelId === 'call_john') {

			// Execute the dial function and pass the URI for John Doe
			dial('jdoe@cll-collab.internal')
		}
	});
}

listenToGui();