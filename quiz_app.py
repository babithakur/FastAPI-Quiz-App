import requests
import json
from pyfiglet import Figlet

def check_valid_input(chars: list[str], user_input: str):
    if user_input not in chars:
        try:
            user_input = input("Invalid input! Please try again: ")
            check_valid_input(chars, user_input)
        except KeyboardInterrupt:
            print("\nSee you again :)")
            exit()
    return True

score = 0

def ask_question(num: int):
    global score
    if num > 10:
        print(f"Thanks for playing! Here's your final score: {score}")
        exit()
    try:
        question_req = requests.get(f"http://127.0.0.1:8000/questions/{num}")
    except:
        print("Sorry! An error occured :(")
        exit()
    alpha_list = ["a", "b", "c", "d"]
    alpha_list_index = 0
    correct_alpha = alpha_list[alpha_list_index]
    correct_answer = question_req.json()['answer']

    print(f"{num}. {question_req.json()['question']}")
    for option in question_req.json()['options']:
        if option == correct_answer:
            correct_alpha = alpha_list[alpha_list_index]
        print(f"{alpha_list[alpha_list_index].upper()}. {option}")
        alpha_list_index+=1
    try:
        answer = input("Your answer: ").rstrip().lower()
    except KeyboardInterrupt:
        print("\nThanks for playing! See you :)")
        exit()
    if check_valid_input(alpha_list, answer):
        if answer == correct_alpha:
            score += 1
            print("Congrats! It's the right answer.\n")
        else:
            print(f"Oops! It's incorrect. The correct answer is {correct_answer}.\n")
    ask_question(num+1)

if __name__ == '__main__':
    print(Figlet().renderText('BASIC IT QUIZ'))
    print("Welcome to the basic computer science quiz!\n\
        Here are some rules to be followed:\n\
        1. Enter a, b, c, d as your answer from the given options. The characters are case insensitive.\n\
        2. Press Ctrl+C if you want to quit the quiz.\n\
        3. Your final score will be displayed at the end of the quiz. There are total 10 questions.\n")
    try:
        play = input("Are you ready to play? Type 'y' to continue: ")
    except KeyboardInterrupt:
        print("\nSee you again :)")
        exit()
    if check_valid_input(['y'], play):
        ask_question(1)





