from flask import Flask, make_response, redirect, session, url_for, render_template, request
import random
import csv
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
import smtplib
from email.mime.text import MIMEText
import os
import wtforms
import wtforms.validators


# import google_auth_oauthlib.flow
# import googleapiclient.discovery
# import googleapiclient.errors


app = Flask(__name__)
app.secret_key='dev'
Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')


# class ContactForm(FlaskForm):
#     name = wtforms.StringField('Name', [wtforms.validators.DataRequired()])
#     email = wtforms.StringField('Email', [wtforms.validators.Email(), wtforms.validators.DataRequired()])
#     message = wtforms.TextAreaField('Message', [wtforms.validators.DataRequired()])
#     submit = wtforms.SubmitField('Submit')

# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     form = ContactForm()
#     if form.validate_on_submit():
#         # Process the form data
#         name = form.name.data
#         email = form.email.data
#         message = form.message.data
#         # Here you can add code to save the data or send an email
#         return redirect(url_for('index'))
#     return render_template('contact.html', form=form)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Email configuration
        sender_email = email
        receiver_email = "chmartinez2014@gmail.com"
        subject = "New Contact Form Submission"
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"

        # Create the email message
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        # Send the email
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, os.getenv("EMAIL_PASSWORD"))
                server.sendmail(sender_email, receiver_email, msg.as_string())
        except Exception as e:
            print(f"Error sending email: {e}")
        return redirect(url_for('index'))
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')


    
@app.route('/get_sessions/<app>')
def get_sessions(app):
    if app == 'guess':
        session['guesses'] = [] 
        resp = make_response(redirect(url_for('guess')))
        resp.set_cookie('random_number', str(random.randint(1,10)))
        session['attempt'] = -1
    elif app == 'phrase':
        resp = make_response(redirect(url_for('phrase')))
        session['guesses'] = [] 
        session['mistakes'] = 0
        phrases = ['Come at me bro','as easy as pie','Epic Sax Guy','Hello world','One of a kind', 'All or Nothing', 'Back to Square One', 'Barking Up The Wrong Tree', 'Beat Around the Bush', 'Better Late Than Never', 'Bite the Bullet', 'Break The Ice', 'Call It A Day', 'Cut To The Chase', 'Cutting Corners', 'Easy As Pie', 'Every Cloud Has A Silver Lining', 'Get Out Of Hand', 'Get Something Out Of Your System', 'Get Your Act Together', 'Give Someone The Cold Shoulder', 'Go Back To The Drawing Board', 'Hang In There', 'Hit The Sack', 'It Takes Two To Tango', 'Jump On The Bandwagon', 'Keep Your Chin Up', 'Kill Two Birds With One Stone', 'Let Someone Off The Hook', 'Make A Long Story Short', 'Miss The Boat', 'No Pain, No Gain', 'On The Ball', 'Pull Yourself Together', 'So Far So Good', 'Speak Of The Devil', 'The Best Of Both Worlds', 'Time Flies When Youre Having Fun', 'Under The Weather', 'You Can Say That Again', 'Your Guess Is As Good As Mine']
        session['phrase'] = random.choice(phrases)
        session['output'] = ["\u25A1" if letter.isalpha() else " " for letter in session['phrase']]
    elif app == 'atm':
        resp = make_response(redirect(url_for('atm')))
        session['saving'] = '10000'
        session['checking'] = '500'
    return resp


@app.route('/guess')
def guess():

    # guesses 
    guesses = session.get('guesses', [])
    attempts = session.get('attempt', 0)
    try:
        random_number = int(request.cookies.get('random_number'))
        if random_number == 10:
            random_number = 10
        print("random number: ", random_number)
        print(type(random_number))
        attempts += 1
    except (TypeError, ValueError):
        random_number = 0
    session['attempt'] = attempts
    guess = request.args.get('guess','')
    try:
        guess = int(guess)
    except ValueError:
          print("Invalid guess: ", guess, ValueError)
          guess = None

    if guess is not None:
        guesses.append(guess)
    session['guesses'] = guesses
    print(guesses)

    print("random number: ", random_number)
    print("guess: ", guess)
    if random_number == 0:
        return "Cookies Disabled: Please enable cookies in your browser's settings to play this game."
    if guess == random_number:
        session['attempt'] = -1
    return render_template('guess.html', guess=guess, random_number=random_number, attempts=attempts, guesses=guesses)


@app.route('/phrase')
def phrase():
    # get session variables

    # guesses 
    guesses = session['guesses']
    # phrase
    phrase = session['phrase']
    # mistakes
    mistakes = session['mistakes']
    # output
    output = session['output']

    # get guess
    guess = request.args.get('guess' ,'').lower()
    # print("Guess: ", guess)
    if guess != '':
        # update guesses
        guesses.append(guess)
        session['guesses'] = guesses
    
    # update output
    is_mistake = True
    for i, letter in enumerate(phrase):
        if guess == letter.lower():
            is_mistake = False
            if letter.isupper():
                output[i] = guess.upper()
            else:
                output[i] = guess
    if guess == '':
        is_mistake = False
    # increment mistakes
    if is_mistake:
        mistakes += 1
        session['mistakes'] = mistakes

    # check mistakes
    if mistakes >= 6:
        return render_template('lost.html', phrase=phrase)
    
    string_output = ''.join(map(str, output))
    if str(string_output) == phrase:
        return render_template('winner.html', phrase=phrase)

    # debug 
    # print("guesses:", guesses)
    # print('Phrase: ', phrase)
    # print('Mistakes: ', mistakes)
    # print("Output: ", output)
    return render_template('phrase.html', output=output, guesses=guesses, mistakes=mistakes) 



@app.route('/credit-card-validator', methods=('POST', 'GET'))
def credit_card_validator():
    DISCOVER = 16
    MASTERCARD = 16
    AMERICAN_EXPRESS = 15
    VISA = 13, 16
    card_type = None
    credit_card_number = ''
    
    if request.method == 'POST':
        try:
            credit_card_number = request.form.get('ccn')
        except ValueError:
            pass
        credit_card_number = ''.join(credit_card_number.split())
        if credit_card_number.isdigit() == False:
            return render_template('credit.html', card_type='Invalid')
            

    if len(credit_card_number) == MASTERCARD and credit_card_number[0] == '5' and (credit_card_number[1] >= '1' or credit_card_number <= '5'):
        card_type = "MASTERCARD"
    elif len(credit_card_number) == DISCOVER and credit_card_number[0] == '6':
        card_type = "DISCOVER"
    elif len(credit_card_number) == AMERICAN_EXPRESS and credit_card_number[0] == '3' and (credit_card_number[1] == '4' or credit_card_number[1] == '7'):
        card_type = "AMEX"
    elif len(credit_card_number) == VISA[0] or len(credit_card_number) == VISA[1] and credit_card_number[0] == '4':
        card_type = "VISA"
    elif credit_card_number == '':
        return render_template('credit.html', card_type=None)


    every_other = []
    for i in range(2, len(credit_card_number)+1, 2):
        every_other.append(credit_card_number[-i])

    other_every = []
    for i in range(1, len(credit_card_number)+1, 2):
        other_every.append(int(credit_card_number[-i]))

    for f in range(len(every_other)):
        every_other[f] = int(every_other[f]) * 2
        every_other[f] = str(every_other[f])

    products_digits = []

    for i in range(len(every_other)):
        for f in range(len(every_other[i])):
            products_digits.append(int(every_other[i][f]))

    total = sum(products_digits) + sum(other_every)

    total = str(total)
    if total[-1] == '0':
        return render_template('credit.html', card_type=card_type)
    else:
        return render_template('credit.html', card_type='Invalid')



@app.route('/readability', methods=('POST', 'GET'))
def readability():
    # get user input 
    text = request.form.get('text', '')

    # get list of chars from user input
    list_of_chars = []
    for i in text:
        list_of_chars.append(i)

    # set variables
    letters = 0
    words = 0
    sentences = 0

    # count sentences, letters, and words
    for char in list_of_chars:
        if char == '.' or char == '!' or char == '?':
            sentences += 1
        elif char.isalpha():
            letters +=1
        elif char == ' ':
            words += 1
    words += 1

    # calculate ratios
    L = letters / words * 100
    S = sentences / words * 100
    # calculate index
    index = round(0.0588 * L - 0.296 * S -15.8)
    print(index)
    return render_template('readability.html', index=index)


@app.route('/atm', methods=('POST', 'GET'))
def atm():
    if request.method == 'POST':
        return render_template('atm.html')

        # amount = request.form.get('amount')
        # action = request.form.get('action')
        # if action == 'deposit':
        #     if request.form.get('account') == 'savings':
        #         session['savings'] += int(amount)
        #     elif request.form.get('account') == 'checking':
        #         session['checking'] += int(amount)
        # elif action == 'withdraw':
        #     if request.form.get('account') == 'savings':
        #         if session['savings'] - int(amount) < 0:
        #             return render_template('atm.html', error='Insufficient Funds')
        #         else:
        #             session['savings'] -= int(amount)
        #     elif request.form.get('account') == 'checking':
        #         if session['checking'] - int(amount) < 0:
        #             return render_template('atm.html', error='Insufficient Funds')
        #         else:
        #             session['checking'] -= int(amount)
        # return render_template('atm.html', savings=session['savings'], checking=session['checking'])

    elif request.method == 'GET':
        saving = session.get('saving')
        checking = session.get('checking')

        print(saving, checking)
        return render_template('atm.html', saving=saving, checking=checking)


@app.route('/fifa-world-cup', methods=('POST', 'GET'))
def fifa_world_cup():

    if request.method == 'POST':

        # Number of simluations to run
        N = int(request.form.get('simulations'))

        def main():

            teams = []
            # TODO: Read teams into memory from file
            with open("2018m.csv", 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    teams.append({'team': row['team'], 'rating': int(row['rating'])})


            counts = {}
            # TODO: Simulate N tournaments and keep track of win counts
            for x in range(N):
                winner = simulate_tournament(teams)
                if winner in counts:
                    counts[winner] += 1
                else:
                    counts[winner] = 1

            # Print each team's chances of winning, according to simulation
            chance = {}
            for team in sorted(counts, key=lambda team: counts[team], reverse = True):
                chance[team] = f"{counts[team] * 100 / N:.2f}"

            return chance, counts


        def simulate_game(team1, team2):
            """Simulate a game. Return True if team1 wins, False otherwise."""
            rating1 = team1["rating"]
            rating2 = team2["rating"]
            probability = 1 / (1 + 10 ** ((rating2 - rating1) / 600))
            return random.random() < probability


        def simulate_round(teams):
            """Simulate a round. Return a list of winning teams."""
            winners = []

            # Simulate games for all pairs of teams
            for i in range(0, len(teams), 2):
                if simulate_game(teams[i], teams[i + 1]):
                    winners.append(teams[i])
                else:
                    winners.append(teams[i + 1])

            return winners


        def simulate_tournament(teams):
            """Simulate a tournament. Return name of winning team."""
            # TODO
            winners = simulate_round(teams)
            while len(winners) > 1:
                winners = simulate_round(winners)
            return winners[0]['team']

        chance, counts = main()
        
        stats = []
        for team in sorted(counts, key=lambda team: counts[team], reverse = True):
            stats.append({'team': team, 'chance': chance[team], 'count': counts[team]})
        print("stats", stats)
        
        return render_template('fifa-world-cup.html', stats=stats)

    elif request.method == 'GET':
        return render_template('fifa-world-cup.html')




# @app.route('/youtube')
# def youtube():

#     scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

#     # Disable OAuthlib's HTTPS verification when running locally.
#     # *DO NOT* leave this option enabled in production.
#     os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

#     api_service_name = "youtube"
#     api_version = "v3"
#     client_secrets_file = "C:\Code\Python\Flask App\client_secret_224964196123-6j9ovbrq8a1p3dp69nia0sicsun4d8k8.apps.googleusercontent.com.json"

#     # Get credentials and create an API client
#     flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
#     credentials = flow.run_console()
#     youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

#     request = youtube.channels().list(
#         part="snippet,contentDetails,statistics",
#         id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
#     )
#     response = request.execute()

#     print(response)
#     # key = 'AIzaSyCjPdBemzmrp2p5dV2AP_0wp2ennVbeSdo'
#     return render_template('youtube.html')


if __name__ == '__main__':
    app.run(debug=True)


