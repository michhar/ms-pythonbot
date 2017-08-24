## MS-Pythonbot tl;dr

A first stab at a Microsoft Bot Framework Python bot using the REST API.  See below on how it works and how to run it locally with the Emulator.

## How it works

[Flask-OpenID](https://github.com/puiterwijk/flask-oidc) is used for authentication (decorates the routing function in the bot app - see code).

## How to run

This example is a "Hi there!" Python bot using the [Flask microframework](http://flask.pocoo.org/) to work with the Bot Framework on Azure or even just locally with the Bot Framework Emulator (recommended to use for testing and dev).  It leverages callback logic inspired by the [dash project](https://github.com/plotly/dash) from plotly.

#### Setup

NOTE:  The flask app tests to see which OS the app is on and decides how to call the necessary dependencies.

* Download the Bot Framework Emulator for local testing (https://github.com/Microsoft/BotFramework-Emulator#download) - multiple OS compatibility.

This is OS-agnostic.

#### Run

From the `ms-pythonbot` base folder:

    python runserver.py

#### Test locally in emulator

1. Open up the BF Emulator (usually called `botframework-emulator` on your system)
1. Click on the "Enter your endpoint URL" and select or type in `http://localhost:3978/api/messages`
2. Leave the "Microsoft App ID" and "Microsoft App Password" blank unless you have these and have ngrok set up
3. Click "CONNECT"

You should see in the Log window a "conversationUpdate" appear twice with no errors.  If there's an error ensure you have the `runserver.py` script going.

## TODO

1.  Deploy to Azure
2.  Add task queueing and asynchronousness would be good, but not needed here.  It just might not scale very well, but that needs testing.

## Future directions

Feed back into and leverage a python botframework wrapper.

## Contributing


1.  Fork this repo and clone locally
2.  Write some awesome addition, feature or update 
3.  Check in your assets to your fork on GitHub
4.  Create a Pull Request to the origin (this repo)
5.  When reviewers have approved, they will do a `merge`
6.  Pat yourself on the back for a job well done!

Feel free to create any Issues on this repo for your tasks, problems or to show others what you are working on.  You can even attach an Issue to a Pull Request with the [#num] formatting.
