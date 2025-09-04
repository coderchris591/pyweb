import os
from flask import Flask, make_response, redirect, session, url_for, render_template, request
import random
import csv
from flask import Flask
# from flask_bootstrap import Bootstrap
# from flask_wtf import FlaskForm
from email.mime.text import MIMEText
# import wtforms.validators


app = Flask(__name__)
app.secret_key='dev'
# Bootstrap(app)
   
@app.route('/')
def index():
    return render_template('index.html')



    
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
        phrases = ['Pack your bags', 'Catch a flight', 'Hit the road', 'Travel light', 'Journey of a lifetime', 'Lost in translation', 'Around the world', 'Bon voyage', 'Wanderlust adventure']
        session['phrase'] = random.choice(phrases)
        session['output'] = ["\u25A1" if letter.isalpha() else " " for letter in session['phrase']]
    elif app == 'atm':
        resp = make_response(redirect(url_for('atm')))
        session['saving'] = '10000'
        session['checking'] = '500'
    elif app == 'blackjack':
        resp = make_response(redirect(url_for('blackjack')))
        session['deck'] = []
        session['player_hand'] = []
        session['dealer_hand'] = []
        session['game_over'] = False
        session['hits'] = 0
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

@app.route('/reset_guess')
def reset_guess():
    session.pop('guesses', None)
    session['attempt'] = 0
    resp = make_response(redirect(url_for('guess')))
    resp.set_cookie('random_number', str(random.randint(1, 20)))  # or your range
    return resp

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
        return render_template('phrase.html', game_over=True, lost=True, phrase=phrase)
    
    string_output = ''.join(map(str, output))
    if str(string_output) == phrase:
        return render_template('phrase.html', game_over=True, lost=False, phrase=phrase)

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



# @app.route('/readability', methods=('POST', 'GET'))
# def readability():
#     # get user input 
#     text = request.form.get('text', '')

#     # get list of chars from user input
#     list_of_chars = []
#     for i in text:
#         list_of_chars.append(i)

#     # set variables
#     letters = 0
#     words = 0
#     sentences = 0

#     # count sentences, letters, and words
#     for char in list_of_chars:
#         if char == '.' or char == '!' or char == '?':
#             sentences += 1
#         elif char.isalpha():
#             letters +=1
#         elif char == ' ':
#             words += 1
#     words += 1

#     # calculate ratios
#     L = letters / words * 100
#     S = sentences / words * 100
#     # calculate index
#     index = round(0.0588 * L - 0.296 * S -15.8)
#     print(index)
#     return render_template('readability.html', index=index)


# @app.route('/atm', methods=('POST', 'GET'))
# def atm():
#     if request.method == 'POST':
#         return render_template('atm.html')

#         # amount = request.form.get('amount')
#         # action = request.form.get('action')
#         # if action == 'deposit':
#         #     if request.form.get('account') == 'savings':
#         #         session['savings'] += int(amount)
#         #     elif request.form.get('account') == 'checking':
#         #         session['checking'] += int(amount)
#         # elif action == 'withdraw':
#         #     if request.form.get('account') == 'savings':
#         #         if session['savings'] - int(amount) < 0:
#         #             return render_template('atm.html', error='Insufficient Funds')
#         #         else:
#         #             session['savings'] -= int(amount)
#         #     elif request.form.get('account') == 'checking':
#         #         if session['checking'] - int(amount) < 0:
#         #             return render_template('atm.html', error='Insufficient Funds')
#         #         else:
#         #             session['checking'] -= int(amount)
#         # return render_template('atm.html', savings=session['savings'], checking=session['checking'])

#     elif request.method == 'GET':
#         saving = session.get('saving')
#         checking = session.get('checking')

#         print(saving, checking)
#         return render_template('atm.html', saving=saving, checking=checking)



# @app.route('/fifa-world-cup', methods=('POST', 'GET'))
# def fifa_world_cup():

#     if request.method == 'POST':

#         # Number of simluations to run
#         N = int(request.form.get('simulations'))

#         def main():

#             teams = []
#             # Read teams into memory from file
#             try:
#                 with open(os.path.join(os.getcwd(), "2018m.csv"), 'r') as file:
#                     reader = csv.DictReader(file)
#                     for row in reader:
#                         teams.append({'team': row['team'], 'rating': int(row['rating'])})
#             except FileNotFoundError:
#                 return "Could not find 2018m.csv"


#             counts = {}
#             # TODO: Simulate N tournaments and keep track of win counts
#             for x in range(N):
#                 winner = simulate_tournament(teams)
#                 if winner in counts:
#                     counts[winner] += 1
#                 else:
#                     counts[winner] = 1

#             # Print each team's chances of winning, according to simulation
#             chance = {}
#             for team in sorted(counts, key=lambda team: counts[team], reverse = True):
#                 chance[team] = f"{counts[team] * 100 / N:.2f}"

#             return chance, counts


#         def simulate_game(team1, team2):
#             """Simulate a game. Return True if team1 wins, False otherwise."""
#             rating1 = team1["rating"]
#             rating2 = team2["rating"]
#             probability = 1 / (1 + 10 ** ((rating2 - rating1) / 600))
#             return random.random() < probability


#         def simulate_round(teams):
#             """Simulate a round. Return a list of winning teams."""
#             winners = []

#             # Simulate games for all pairs of teams
#             for i in range(0, len(teams), 2):
#                 if simulate_game(teams[i], teams[i + 1]):
#                     winners.append(teams[i])
#                 else:
#                     winners.append(teams[i + 1])

#             return winners


#         def simulate_tournament(teams):
#             """Simulate a tournament. Return name of winning team."""
#             # TODO
#             winners = simulate_round(teams)
#             while len(winners) > 1:
#                 winners = simulate_round(winners)
#             return winners[0]['team']

#         chance, counts = main()
        
#         stats = []
#         for team in sorted(counts, key=lambda team: counts[team], reverse = True):
#             stats.append({'team': team, 'chance': chance[team], 'count': counts[team]})
#         print("stats", stats)
        
#         return render_template('fifa-world-cup.html', stats=stats)

#     elif request.method == 'GET':
#         return render_template('fifa-world-cup.html')







# @app.route('/graph-theory', methods=('POST', 'GET'))
# def graph_theory():

#     def get_cartesian_product(A, B):
#             cartesian_product = []
#             for a in A:
#                 for b in B:
#                     if a.isnumeric() and b.isnumeric() and (a, b) not in cartesian_product:
#                         cartesian_product.append((int(a), int(b)))
#             if len(cartesian_product) == 0:
#                 print("\nEmpty Set: \u2205")
#                 return
#             print("\nCartesian Product: { ", end="")
#             for i in range(len(cartesian_product)):
#                 if i == len(cartesian_product) - 1:
#                     print(cartesian_product[i], end="")
#                 else:
#                     print(cartesian_product[i], end=", ")
#             print(" }")
#             return cartesian_product
    

#     def get_union(A, B):
#             union = A + B
#             print(union)
#             for i in range(len(union)):
#                 union[i] = int(union[i])
#             union = list(set(union))
#             if len(union) == 0:
#                 # print("\nEmpty Set: \u2205")
#                 return ['\u2205']
#             union.sort()
            
#             # print("\nUnion: { ", end="")
#             # for i in range(len(union)):
#             #     if i == len(union) - 1:
#             #         print(union[i], end="")
#             #     else:
#             #         print(union[i], end=", ")
#             # print(" }")
#             return union
    

#     def get_intersection(A,B):
#             interesction = []
#             for a in A:
#                 print(a)
#                 if a in B and a not in interesction and a.isnumeric():
#                     interesction.append(a)
#             for b in B:
#                 if b in B and b not in interesction and b.isnumeric():
#                     interesction.append(b)
#                 if len(interesction) == 0:
#                     print("\nEmpty Set: \u2205")
#                     return
#             for i in range(len(interesction)):
#                 interesction[i] = int(interesction[i])
#             interesction.sort()
#             print("\nIntersection: { ", end="")
#             for i in range(len(interesction)):
#                 if i == len(interesction) - 1:
#                     print(interesction[i], end="")
#                 else:
#                     print(i, end=", ")
#             print("}")
#             return interesction

    
#     if request.method == 'POST':
#         # get user input 
#         A = request.form.get('setA')
#         B = request.form.get('setB')
#         choice = request.form.get('section')
#         A = A.replace("{", "").replace("}", "").replace(" ", "").split(",")
#         B = B.replace("{", "").replace("}", "").replace(" ", "").split(",")
#         if choice == 'cartesianProduct':
#             type = 'Cartesian Product'
#             result = get_cartesian_product(A, B)
#         elif choice == 'union':
#             type = 'Union'
#             result = get_union(A, B)
#         elif choice == 'intersection':
#             type = 'Intersection'
#             result = get_intersection(A, B)
#         return render_template('graph-theory.html', result=result, type=type, setA = A, setB = B)
#     else:
#         return render_template('graph-theory.html')
    


# @app.route('/blog', methods=('POST', 'GET'))
# def blog():
#     return render_template('blog.html')




# # @app.route('/youtube')
# # def youtube():

# #     scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

# #     # Disable OAuthlib's HTTPS verification when running locally.
# #     # *DO NOT* leave this option enabled in production.
# #     os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# #     api_service_name = "youtube"
# #     api_version = "v3"
# #     client_secrets_file = "C:\Code\Python\Flask App\client_secret_224964196123-6j9ovbrq8a1p3dp69nia0sicsun4d8k8.apps.googleusercontent.com.json"

# #     # Get credentials and create an API client
# #     flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
# #     credentials = flow.run_console()
# #     youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

# #     request = youtube.channels().list(
# #         part="snippet,contentDetails,statistics",
# #         id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
# #     )
# #     response = request.execute()

# #     print(response)
# #     # key = 'AIzaSyCjPdBemzmrp2p5dV2AP_0wp2ennVbeSdo'
# #     return render_template('youtube.html')


# @app.route('/blackjack', methods=('POST', 'GET'))
# def blackjack():

#     if request.method == 'POST':
#         print("POST request for blackjack")
#         action = request.form.get('action')

        
#         if action == 'hit':
#             pass
        
#     else:
#         print("GET request for blackjack")
#         deck = get_shuffled_deck()
#         session['deck'] = deck

#         player_hand = session['player_hand'] = []
#         dealer_hand = session['dealer_hand'] = []

#         # Deal initial cards
#         for _ in range(2):
#             player_hand.append(deck.pop())
#             dealer_hand.append(deck.pop())
#         return render_template('blackjack.html')


# def get_shuffled_deck():

#         suits = {'hearts', 'diams', 'clubs', 'spades'}
#         ranks = {'2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'}
#         deck = []

#         for suit in suits:
#             for rank in ranks:
#                 deck.append({'suit': suit, 'rank': rank})
#         random.shuffle(deck)
#         return deck





if __name__ == '__main__':
    app.run(debug=True)


