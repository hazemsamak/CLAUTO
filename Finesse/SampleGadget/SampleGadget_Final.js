var finesse = finesse || {};
finesse.gadget = finesse.gadget || {};
finesse.container = finesse.container || {};
clientLogs = finesse.cslogger.ClientLogger || {};  // for logging

/**
 * The following comment prevents JSLint errors concerning the logFinesse function being undefined.
 * logFinesse is defined in Log.js, which should also be included by gadget the includes this file.
 */
/*global logFinesse */

/** @namespace */
finesse.modules = finesse.modules || {};
finesse.modules.SampleGadget = (function ($) {
    var user, states, dialogs, clientlogs,

    /**
     * Populates the fields in the gadget with data
     */
    render = function () {
        var currentState = user.getState();

        // Examples of getting data from the User object (GET)
        $("#userId").text(user.getId());
        $("#firstName").text(user.getFirstName());
        $("#lastName").text(user.getLastName());
        if (user.hasSupervisorRole()) {
            $("#userRole").text('Supervisor');
        } else {
            $("#userRole").text('Agent');
        }
        $("#extension").text(user.getExtension());
        $("#userState").text(currentState);

        // Example of setting the user state (PUT)
        if (currentState === states.NOT_READY) {
            $("#goReady").show();
            $("#goNotReady").hide();
        } else if (currentState === states.READY) {
            $("#goNotReady").show();
            $("#goReady").hide();
        } else {
            $("#goNotReady").hide();
            $("#goReady").hide();
        }
        
        gadgets.window.adjustHeight();
    },

    displayCall = function (dialog) {
        var callVars = dialog.getMediaProperties();

        // Examples of getting data from the Dialog object (GET)
        $("#callType").text(dialog.getMediaProperties().callType);
        $("#fromAddress").text(dialog.getFromAddress());
        $("#toAddress").text(dialog.getToAddress());
        $("#callState").text(dialog.getState());

        // Hide the make call button when the user is on a call
        $("#makeCallButton").hide();
    },

    _processCall = function (dialog) {
        displayCall(dialog);
    },

    /**
     *  Handler for additions to the Dialogs collection object. This will occur when a new
     *  Dialog is created on the Finesse server for this user.
     */
    handleNewDialog = function(dialog) {
        // call the displayCall handler
        displayCall(dialog);

        // add a dialog change handler in case the callvars didn't arrive yet
        dialog.addHandler('change', _processCall);
    },
     
    /**
     *  Handler for deletions from the Dialogs collection object for this user. This will occur
     *  when a Dialog is removed from this user's collection (example, end call)
     */
    handleEndDialog = function(dialog) {
        // Clear the fields when the call is ended
        $("#callType").text("");
        $("#fromAddress").text("");
        $("#toAddress").text("");
        $("#callState").text("");

        // Show the make call button when the call is ended
        $("#makeCallButton").show();
    },

    /**
     * Handler for makeCall when successful.
     */
    makeCallSuccess = function(rsp) { },
    
    /**
     * Handler for makeCall when error occurs.
     */
    makeCallError = function(rsp) { },

    /**
     * Handler for the onLoad of a User object. This occurs when the User object is initially read
     * from the Finesse server. Any once only initialization should be done within this function.
     */
    handleUserLoad = function (userevent) {
        // Get an instance of the dialogs collection and register handlers for dialog additions and
        // removals
        dialogs = user.getDialogs( {
            onCollectionAdd : handleNewDialog,
            onCollectionDelete : handleEndDialog
        });

        render();
    },
      
    /**
     *  Handler for all User updates
     */
    handleUserChange = function(userevent) {
        render();
    };

    /** @scope finesse.modules.SampleGadget */
    return {
        /**
         * Sets the user state
         */
        setUserState : function (state) {
            clientLogs.log("setUserState(): The user's current state is: " + state);
            if (state === 'READY') {
                user.setState(states.READY);
            } else if (state === 'NOT_READY') {
                user.setState(states.NOT_READY);
            }
        },

        /**
         * Make a call to the number
         */
        makeCall : function (number) {
            clientLogs.log("makeCall(): Making a call to " + number);
            // Example of the user make call method
            user.makeCall(number, {
                success: makeCallSuccess,
                error: makeCallError
            });

            // Hide the button after making the call
            $("#makeCallButton").hide();
        },

        /**
         * Performs all initialization for this gadget
         */
        init : function () {
            var cfg = finesse.gadget.Config;

            clientLogs = finesse.cslogger.ClientLogger;  // declare clientLogs

            gadgets.window.adjustHeight();

            // Initiate the ClientServices and load the user object. ClientServices are
            // initialized with a reference to the current configuration.
            finesse.clientservices.ClientServices.init(cfg, false);

            // Initiate the ClientLogs. The gadget id will be logged as a part of the message
            clientLogs.init(gadgets.Hub, "LearningSampleGadget");

            user = new finesse.restservices.User({
                id: cfg.id, 
                onLoad : handleUserLoad,
                onChange : handleUserChange
            });

            states = finesse.restservices.User.States;
            
            // Initiate the ContainerServices and add a handler for when the tab is visible
            // to adjust the height of this gadget in case the tab was not visible
            // when the html was rendered (adjustHeight only works when tab is visible)
            containerServices = finesse.containerservices.ContainerServices.init();
            containerServices.addHandler(finesse.containerservices.ContainerServices.Topics.ACTIVE_TAB, function() {
                clientLogs.log("Gadget is now visible");  // log to Finesse logger
                // automatically adjust the height of the gadget to show the html
                gadgets.window.adjustHeight();
            });
            containerServices.makeActiveTabReq();
        }
    };
}(jQuery));