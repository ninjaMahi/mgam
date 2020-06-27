import random

user_carry_on = ""
lives = 8
letter_score = 0
file = open("words.txt", "r")
line_list = []
for line in file:
    line_list.append(line)
    randomIndex = random.randint(1, 200)

randomline = line_list[randomIndex]
Correct_letters_guesed = ["_", "_", "_", "_", "_","_"]
Incorrect_letters_guesed = []
Letter_List = list(randomline)
letter_word= str(randomline)

            

while (lives != 0 or letter_score == 6):
    user_guess = input("please guess a letter : ")
    if user_guess not in Letter_List :
        Incorrect_letters_guesed.append(user_guess)
        lives = lives - 1
        str_lives = str(lives)
        print("Unlucky your guess was incorrect.You know have " + str_lives + " lives left")
        print("Incorrect letters guessed( " + str(Incorrect_letters_guesed) + ")")
        print("correct letters guessed( " + str(Correct_letters_guesed) + ")")
    elif user_guess  in Letter_List :
        for i in range(6) :
            if user_guess == Letter_List[i] :
                Correct_letters_guesed[i] = Letter_List[i]
                Letter_List[i]= "_"
        str_lives = str(lives)
        print(" your guess was correct.You still have " + str_lives + " lives left")
        print("correct letters guessed( " + str(Correct_letters_guesed) + ")")
        print("Incorrect letters guessed( " + str(Incorrect_letters_guesed) + ")")
        letter_score += 1
    
    if lives == 0 :
        print("you have lost you have no lives left" )
        print("Correct word was : "+letter_word)
        break
        
    if letter_score == 6:
        print("You have won ")
        user_carry_on = input("would you like to carry(c) on or go to the menu(m) ")
        break




