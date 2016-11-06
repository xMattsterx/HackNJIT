from __future__ import print_function
import random


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the number guessing game. I will roll one or two dice." \
                    "You will guess the number that was rolled." \
                    "How many dice do you want to roll?"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "How many dice do you want to roll?"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for playing my number guessing game."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def create_number_of_dice_attributes(number_of_dice):
    return {"numberOfDice": number_of_dice}

def create_guess_attributes(guess):
    return {"userGuess": guess}

def set_number_of_dice_in_session(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = None

    if 'NumberOfDice' in intent['slots']:
        number_of_dice = intent['slots']['NumberOfDice']['value']
        session_attributes = create_number_of_dice_attributes(number_of_dice)
        speech_output = "I will roll " + number_of_dice + " dice." \
                        "Please make a guess by saying I guess number."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_guess_in_session(intent, session):
    """ Sets the range in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = None

    if 'Guess' in intent['slots']:
        guess = intent['slots']['Guess']['value']
        session_attributes = create_guess_attributes(guess)
        speech_output = "You guessed " + guess + "Please say ask me what the results are."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_guess_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "numberOfDice" in session.get('attributes', {}):
        number_of_dice = session['attributes']['numberOfDice']
        
        if number_of_dice == 1:
            numberRolled = random.randInt(1,6)

            if guess == numberRolled:
                speech_output = "You guess correctly. Congratulations."
                should_end_session = True
            else:
              speech_output = "You guess incorrectly. Sorry."

        else:
            numberRolled = random.randInt(2,12)
            
            if guess == numberRolled:
                speech_output = "You guess correctly. Congratulations."
            else:
              speech_output = "You guess incorrectly. Sorry."

    else:
        speech_output = "I don't know how many dice to roll. I can roll one or two dice."
        should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SetGuess":
        return set_guess_in_session(intent, session)
    elif intent_name == "SetNumberOfDice":
        return set_number_of_dice_in_session(intent, session)
    elif intent_name == "GetResult":
        return get_guess_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])