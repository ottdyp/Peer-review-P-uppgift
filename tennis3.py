import sys
import time
import random
import math
import tkinter as tk
from tkinter import ttk



class Tennisplayer:
    # class for creating Tennisplayer objects with their name and stats
    def __init__(self, name: str, serve_win_prob: float, matches_won: int, matches_played: int):
        self.name = name
        self.serve_win_prob = serve_win_prob
        self.matches_won = matches_won
        self.matches_played = matches_played

    def win_percentage(self):
        # calculates win percentage for Tennisplayer
        if self.matches_played == 0:
            return 0
        return format(self.matches_won / self.matches_played, '.3f')

    def last_name(self):
        # returns last name of player
        last_name = self.name.strip()[2:]
        return last_name


class PlayerDatabase:
    # class for gathering player stats, creating Tennisplayer objects, reuploading to the input-file and displaying players and stats
    def __init__(self, file_path):
        # initializes player database, players are first stored in self.players and then sorted and stored in self.sorted_players
        self.file_path = file_path
        self.players = []
        self.sorted_players = []

    def load_players(self):
        # reads from input-file
        try:
            with open(self.file_path, "r") as file:

                lines = file.readlines()[5:]

                for line in range(0, len(lines), 4):
                    name = lines[line].strip()
                    serve_win_prob = float(lines[line + 1].strip())
                    matches_won = int(lines[line + 2].strip())
                    matches_played = int(lines[line + 3].strip())

                    self.players.append(Tennisplayer(name, serve_win_prob, matches_won, matches_played))

        except FileNotFoundError:
            print("Spelarfilen hittades inte.")
            sys.exit()

        except ValueError:
            print("Felaktigt format i spelarfilen.")
            sys.exit()

        self.sorted_players = sorted(self.players, key=lambda p: p.win_percentage(), reverse=True)

    def update_file(self):
        # updates file with new stats after played matches
        with open("playerdata.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()

            new_document = lines[:5] # keeps the header of the "playerdata.txt" file

            self.sorted_players = sorted(self.players, key = lambda p: p.win_percentage(), reverse = True)

            for player in self.sorted_players:
                new_document.append(player.name + "\n")
                new_document.append(f"{player.serve_win_prob}\n")
                new_document.append(f"{player.matches_won}\n")

                if player != self.sorted_players[-1]: # makes sure there is no blank line added at the end
                    new_document.append(f"{player.matches_played}\n")
                else:
                    new_document.append(f"{player.matches_played}")

        with open("playerdata.txt", "w", encoding="utf-8") as file:
            file.writelines(new_document)

    
    def display_players(self):
        # presents players in toplist based on win percentage 
        print("\n" + 60*"=" + "\n" + "Placering Namn                   Vunna  Spelade  Andel vunna" + "\n" + 60*"=")
        for i, player in enumerate(self.sorted_players, start = 1):
            time.sleep(0.02)
            print(f"{i:^9} {player.name:24} {player.matches_won:<6} {player.matches_played:<8} {player.win_percentage()}")
            

def manual_match(p1_index, p2_index):
    # asks for winner among two players -> the stats for the players are then updated in main() function
    while True:
        try:
            winner_index = int(input("Vem vann? (ange siffran för spelaren)"))
            if winner_index != p1_index and winner_index != p2_index:
                print("Felaktig inmatning. Välj en av spelarna som spelar matchen. (ange siffran)")
            else:    
                break
        except ValueError:
            print("Felaktig inmating. Välj en av spelarna som spelar matchen. (ange siffran)")  
    return winner_index - 1


class SelectionWindow:
    # class for creating selection window for player and delay choice (GUI)
    def __init__(self, sorted_players):
        # initializes selection window for player and delay choice
        self.window = tk.Tk()
        self.window.geometry("550x800") 
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True)
        self.window.title("Player Selection")

        self.sorted_players = sorted_players

        self.player_selections = [] # storage for player selections

        # creates canvas and scrollbar
        self.canvas = tk.Canvas(self.window)
        self.scrollbar = ttk.Scrollbar(master =self.window, orient = "vertical", command = self.canvas.yview)

        # creates frame in canvas
        self.scrollable_frame = ttk.Frame(master = self.canvas)

        # adds the frame to the canvas
        self.canvas.create_window((0, 0), window = self.scrollable_frame, anchor = "nw")

        # confgures the scrollbar
        self.canvas.configure(yscrollcommand = self.scrollbar.set)

        # packs canvas and scrollbar onto the window
        self.canvas.pack(side = "left", fill = "both", expand = True)
        self.scrollbar.pack(side = "right", fill = "y")

        # adds all my content to the frame
        self.add_content()

        # added to make the scrolling work as it should
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))

    def add_content(self):
        # creates header for the page
        tk.Label(self.scrollable_frame, text = "Välj 2 spelare och tidsfördröjning:", font = ("Arial", 14)).pack(pady = 10)
        tk.Label(self.scrollable_frame, text = "Placering  Namn                   Vunna  Spelade  Andel vunna", font = ("Courier", 10, "bold")).pack(fill = "x")

        # creates all the buttons for the players
        for i, player in enumerate(self.sorted_players, start = 1):
            button_text = f"{i:^9} {player.name:24} {player.matches_won:<6} {player.matches_played:<6} {player.win_percentage():>9}"
            player_button = tk.Button(
                self.scrollable_frame,
                text = button_text,
                font = ("Courier", 10), # choose a monospace-font to make formatting easier
                anchor = "w",
                command = lambda i = i: self.click_player(i)
            )
            player_button.pack(fill = "x", pady = 2)

        # adds entry line for delay-input and button to start the match
        delay_frame = ttk.Frame(self.scrollable_frame)
        delay_frame.pack(pady = 10, fill = "x")

        tk.Label(delay_frame, text = "Bestäm fördröjningen (sekunder):", font = ("Arial", 12)).pack(side = "left", padx = 5)
        self.delay_entry = ttk.Entry(delay_frame)
        self.delay_entry.pack(side = "left", padx = 5)

        submit_button = ttk.Button(self.scrollable_frame, text = "Starta Matchen", command = self.submit_selection)
        submit_button.pack(pady=20)

    def click_player(self, player_index):
        # function that is activated by button-click, determines wether the choice is accepted or not, if accepted its added to player_selections
        if len(self.player_selections) < 2:
            player = self.sorted_players[player_index - 1]

            if player not in self.player_selections:
                self.player_selections.append(player)
                print(f"Du valde {player.name}!")
            else:
                print(f"{player.name} är redan vald!")

        else:
            print("Du har redan valt två spelare!")

    def submit_selection(self):
        # function that is activated by clicking submit-button, if all choices are accepted the delay-input is made into an attribute and window is closed
        try:
            if len(self.player_selections) != 2:
                tk.messagebox.showerror("Error", "Välj exakt 2 spelare!")
                return

            delay = float(self.delay_entry.get())
            if delay < 0 or delay > 3:
                tk.messagebox.showerror("Error", "Fördröjningen måste vara mellan 0-3 sekunder!")
                return

            self.delay_selection = delay
            print(f"Valda spelare: {[p.name for p in self.player_selections]}")
            print(f"Vald fördröjning: {delay}")
            self.window.destroy()

        except ValueError:
            tk.messagebox.showerror("Error", "Felaktig fördröjning! Ange en siffra.")


class ScoreDisplay:
    # class for initializing and updating graphic scorecard (GUI)
    def __init__(self, player1, player2, sorted_players):
        # initialize the tkinter window for displaying scores
        self.window = tk.Tk()
        self.window.geometry("1200x200+0+0")
        self.window.title("Scorecard")
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True) # is always infront of other apps
        self.window.bind("<Escape>", lambda event: self.window.quit()) # closes window with Esc
        self.window.overrideredirect(True) # removes titlebar
        self.window.rowconfigure((0, 1), weight = 1, uniform = "a")
        self.window.columnconfigure(1, weight = 5, uniform = "a")
        self.window.columnconfigure((0,2,3,4,5,6), weight = 1, uniform = "a")

        self.player1 = player1
        self.player2 = player2
        self.sorted_players = sorted_players

        # labels for indicating server
        self.serve_1 = ttk.Label(master = self.window, text = "//", font = "Aharoni 45 bold", background = "#185224", foreground = "#f7f7f5", anchor = "center")
        self.serve_1.grid(row = 0, column = 0, sticky = "nwse")

        self.serve_2 = ttk.Label(master = self.window, text = "", font = "Aharoni 45 bold", background = "#185224", foreground = "#f7f7f5", anchor = "center")
        self.serve_2.grid(row = 1, column = 0, sticky = "nwse")

        # labels for player names
        self.name_1 = ttk.Label(master = self.window, text = f"{self.player1.last_name()} ({self.sorted_players.index(self.player1) + 1})".upper(), font = "Aharoni 45 bold", background = "#185224", foreground = "#f7f7f5")
        self.name_1.grid(row = 0, column = 1, sticky = "nwse")

        self.name_2 = ttk.Label(master = self.window, text = f"{self.player2.last_name()} ({self.sorted_players.index(self.player2) + 1})".upper(), font = "Aharoni 45 bold", background = "#185224", foreground = "#f7f7f5")
        self.name_2.grid(row = 1, column = 1, sticky = "nwse")


        # labels for scores
        self.set_1_p1 = ttk.Label(master = self.window, text = "", font = "Aharoni 60 bold", background = "#185224", foreground = "#f7f7f5", anchor = "center")
        self.set_1_p1.grid(row = 0, column = 2, sticky = "nwse")

        self.set_2_p1 = ttk.Label(master = self.window, text = "", font = "Aharoni 60 bold", background = "#185224", foreground = "#f7f7f5", anchor = "center")
        self.set_2_p1.grid(row = 0, column = 3, sticky = "nwse")

        self.set_3_p1 = ttk.Label(master = self.window, text = "", font = "Aharoni 60 bold", background = "#185224", foreground = "#f7f7f5", anchor = "center")
        self.set_3_p1.grid(row = 0, column = 4, sticky = "nwse")

        self.games_p1= ttk.Label(master = self.window, text = "0", font = "Aharoni 60 bold", background = "#88d197", foreground = "#f7f7f5", anchor = "center")
        self.games_p1.grid(row = 0, column = 5, sticky = "nwse")

        self.points_p1 = ttk.Label(master = self.window, text = "0", font = "Aharoni 60 bold", background = "#f7f7f5", foreground = "#404a42", anchor = "center")
        self.points_p1.grid(row = 0, column = 6, sticky = "nwse")

        self.set_1_p2 = ttk.Label(master = self.window, text = "", font = "Aharoni 60 bold", background = "#185224", foreground = "#f7f7f5", anchor = "center")
        self.set_1_p2.grid(row = 1, column = 2, sticky = "nwse")

        self.set_2_p2 = ttk.Label(master = self.window, text = "", font = "Aharoni 60 bold", background = "#185224", foreground = "#f7f7f5", anchor = "center")
        self.set_2_p2.grid(row = 1, column = 3, sticky = "nwse")

        self.set_3_p2 = ttk.Label(master = self.window, text = "", font = "Aharoni 60 bold", background = "#185224", foreground = "#f7f7f5", anchor = "center")
        self.set_3_p2.grid(row = 1, column = 4, sticky = "nwse")

        self.games_p2 = ttk.Label(master = self.window, text = "0", font = "Aharoni 60 bold", background = "#88d197", foreground = "#f7f7f5", anchor = "center")
        self.games_p2.grid(row = 1, column = 5, sticky = "nwse")

        self.points_p2 = ttk.Label(master = self.window, text = "0", font = "Aharoni 60 bold", background = "#f7f7f5", foreground = "#404a42", anchor = "center")
        self.points_p2.grid(row = 1, column = 6, sticky = "nwse")


    def update_point_scores(self, points_server, points_receiver, server):
        # update the point scores displayed on the scorecard
        if server == self.player1:
            self.points_p1.configure(text = f"{points_server}")
            self.points_p2.configure(text = f"{points_receiver}")
        else:
            self.points_p2.configure(text = f"{points_server}")
            self.points_p1.configure(text = f"{points_receiver}")
        self.window.update()


    def update_game_scores(self, games_player1, games_player2):
        # update the game scores displayed on the scorecard
        self.games_p1.configure(text = f"{games_player1}")
        self.games_p2.configure(text = f"{games_player2}")
        self.window.update()

    def update_set_scores(self, games_player1, games_player2):
        # update the set scores displayed on the scorecard
        self.set_1_p1.configure(text = self.set_2_p1.cget("text"))
        self.set_1_p2.configure(text = self.set_2_p2.cget("text"))

        self.set_2_p1.configure(text = self.set_3_p1.cget("text"))
        self.set_2_p2.configure(text = self.set_3_p2.cget("text"))

        self.set_3_p1.configure(text = f"{games_player1}")
        self.set_3_p2.configure(text = f"{games_player2}")
        self.window.update()

    def update_server(self, server):
        # update indicating symbol for server
        if server == self.player1:
            self.serve_1.configure(text = "//")
            self.serve_2.configure(text = "")
        else:
            self.serve_2.configure(text = "//")
            self.serve_1.configure(text = "")
        self.window.update()

    def final_score(self):
        # updates point- and game-scores to display zeros when match is over
        self.points_p1.configure(text = "0")
        self.points_p2.configure(text = "0")

        self.games_p1.configure(text = "0")
        self.games_p2.configure(text = "0")
        self.window.update()


class Match:
    """ class that creates a simulated match between two players. The logic is based on chain iteration, 
        simulate_match() iterates over simulate_set(), which iterates over simulate_game(), which iterates over simulate_point()"""
    def __init__(self, player1, player2, score_display):
        # initializes match between player1 and player2
        self.player1 = player1
        self.player2 = player2
        self.score_display = score_display # helps decide what the functions should do with and without gui

    def simulate_point(self, server, receiver, delay, display_mode = 4):
        # simulates point
        if display_mode == 1:
            time.sleep(delay)
        return server if random.random() < server.serve_win_prob else receiver

    def simulate_game(self, server, receiver, delay, score_display, display_mode = 4):
        # simulates game
        points = {server: 0, receiver: 0}
        point_names = ["0", "15", "30", "40", "Ad"]  # tennis point system

        if display_mode <= 2: # display who serves the game
            time.sleep(delay)
            print(f"\nGamet börjar: {server.last_name()} servar")
        if display_mode == 1: # start each game on 0-0
            time.sleep(delay)
            print(f"Poäng: {server.last_name()} 0 - 0 {receiver.last_name()}")


        while True:

            if score_display != None:
                self.score_display.update_point_scores(point_names[points[server]], point_names[points[receiver]], server)
                time.sleep(delay)

            winner = self.simulate_point(server, receiver, delay, display_mode)
            points[winner] += 1

            # handles case of lost Ad-point
            if points[server] == 4 and points[receiver] == 4:
                points[server] -= 1
                points[receiver] -= 1

            # print current score based on display_mode and game-winning criteria
            if points[server] >= 4 and points[server] - points[receiver] >= 2:
                if display_mode <= 2:  # display game winner after each game 
                    time.sleep(delay)
                    print(f"\n{server.last_name()} vann gamet\n")
                return server
            elif points[receiver] >= 4 and points[receiver] - points[server] >= 2:
                if display_mode <= 2:  # display game winner after each game 
                    time.sleep(delay)
                    print(f"\n{receiver.last_name()} vann gamet\n")
                return receiver
            else:
                if display_mode == 1:  # display scores after each point
                    print(f"Poäng: {server.last_name()} {point_names[points[server]]} - {point_names[points[receiver]]} {receiver.last_name()}")
  

    def simulate_set(self, server, receiver, delay, score_display, display_mode = 4):
        # simulates set
        games = {self.player1: 0, self.player2: 0}

        while True:

            if score_display != None:
                score_display.update_game_scores(games[self.player1], games[self.player2])
                score_display.update_server(server)

            # if the score is 6-6 a deciding game is played
            if games[self.player1] == 6 and games[self.player2] == 6:
                winner = self.simulate_game(server, receiver, delay, score_display, display_mode)
                games[winner] += 1
                if display_mode <= 3:  # for all display_modes
                    time.sleep(delay)
                    print(40*"-" + f"\n{self.player1.last_name()} vann setet\n" + 40*"-")
                return winner, games

            winner = self.simulate_game(server, receiver, delay, score_display, display_mode)
            games[winner] += 1

            # display current set score
            if display_mode <= 2:  # display scores after each game
                time.sleep(delay)
                print(40*"-" + "\n" + f"Game-ställning: {self.player1.last_name()} {games[self.player1]} - {games[self.player2]} {self.player2.last_name()}" + "\n" + 40*"-")

            # change server
            server, receiver = receiver, server

            # player 1 wins set
            if games[self.player1] >= 6 and games[self.player1] - games[self.player2] >= 2:
                if display_mode <= 3:  # for all display_modes
                    time.sleep(delay)
                    print(40*"-" + f"\n{self.player1.last_name()} vann setet\n" + 40*"-")
                return self.player1, games
            # player 2 wins set
            elif games[self.player2] >= 6 and games[self.player2] - games[self.player1] >= 2:
                if display_mode <= 3:  # for all display_modes
                    time.sleep(delay)
                    print(40*"-" + f"\n{self.player2.last_name()} vann setet\n" + 40*"-")
                return self.player2, games

    def simulate_match(self, delay, score_display, display_mode = 4):
        # simulates entire match
        sets_won = {self.player1: 0, self.player2: 0}
        print("\nMatchen börjar!\n")
        print(f"{self.player1.name} vs {self.player2.name}\n")

        # randomize first server
        server, receiver = (self.player1, self.player2) if random.random() < 0.5 else (self.player2, self.player1)
        print(f"{server.last_name()} servar först")


        while sets_won[self.player1] < 2 and sets_won[self.player2] < 2:
            result = self.simulate_set(server, receiver, delay, score_display, display_mode)
            winner = result[0]
            games_player1 = result[1][self.player1]
            games_player2 = result[1][self.player2]
            sets_won[winner] += 1

            if score_display != None:
                score_display.update_set_scores(games_player1, games_player2)

            # display set scores
            if display_mode <= 3: # for all display_modes
                time.sleep(delay)
                print(40*"-" + f"\nSet-ställning: {self.player1.last_name()} {sets_won[self.player1]} - {sets_won[self.player2]} {self.player2.last_name()}\n" + 40*"-")
        
        if score_display != None: # to get the correct format of final score (gui)
            score_display.final_score()
        time.sleep(delay)
        print(40*"=" + f"\nGame, Set and Match {self.player1.last_name() if sets_won[self.player1] == 2 else self.player2.last_name()}!")
        return self.player1 if sets_won[self.player1] == 2 else self.player2


def main():
    # main function that connects all other classes and functions
    while True:
        # create PlayerDatabase object with our file and load players
        database = PlayerDatabase("playerdata.txt")
        database.load_players()


        # choose if you want gui or not 
        scorecard_choice = "nej" # to not get error when match_form == 1 and scorecard_choice isn't defined
        match_form = 2 # in case scorecard_choice = "Ja" --> match_form is undefined
        while True:
            try:
                scorecard_choice = input("\nVill du se poängställningen i en gui? (ja/nej): ").lower().strip()
                if scorecard_choice == "nej":
                    score_display = None
                    database.display_players()
                    break
                elif scorecard_choice == "ja":
                    break
                else:
                    print('Felaktig inmatning. Skriv "ja" eller "nej"')
            except ValueError:
                print('Felaktig inmatning. Skriv "ja" eller "nej"')

        # choose two players to face eachother
        while scorecard_choice == "nej":
            try:
                p1_index = int(input("Välj spelare 1 (ange placering): ").strip()) - 1
                p2_index = int(input("Välj spelare 2 (ange placering): ").strip()) - 1
                if p1_index == p2_index:
                    print("En spelare kan inte spela mot sig själv.")
                    continue
                player1 = database.sorted_players[p1_index]
                player2 = database.sorted_players[p2_index]
                break
            except (ValueError, IndexError):
                print("Felaktigt val av spelare. Välj en siffra mellan 1-50")
                continue
        # choose match form, manual or simulation
        while scorecard_choice == "nej":
            try:
                match_form = int(input("Vill du välja vinnare eller simulera matchen? Ange 1 eller 2. (1: välja vinnare / 2: simulera): "))
                if match_form in [1, 2]:
                    break
                else:
                    print("Felaktig inmatning. Ange 1 eller 2.")
            except ValueError:
                print("Felaktig inmatning. Ange 1 eller 2.")

        # choose time delay between score displays ("while match_form == 2" since only for simulation)
        while scorecard_choice == "nej" and match_form == 2:
            try:
                delay = float(input("Hur många sekunder tidsfördröjning vill du ha mellan poängen? Ange en siffra mellan 0-3: ").strip())
                if 0 <= delay <= 3:
                    break
                else:
                    print("Felaktig inmatning. Ange en siffra mellan 0-3.")
            except ValueError:
                print("Felaktig inmatning. Ange en siffra mellan 0-3.")

        
        display_mode = 4 # to avoid error when a value for display_mode isn't choosen
        # choose display frequency ("while scorecard_choice == "nej"" since not for gui)("while match_form == 2" since only for simulation)
        while scorecard_choice == "nej" and match_form == 2:
            try:
                display_mode = int(input("Välj visningsfrekvens: 1 (Poäng), 2 (Game), 3 (Set): "). strip())
                if display_mode in [1, 2, 3]:
                    break
                else:
                    print("Felaktig inmatning. Ange 1, 2 eller 3.")
            except ValueError:
                print("Felaktig inmatning. Ange 1, 2 eller 3.")

        # choose winner
        if match_form == 1:
            winner_index = manual_match(p1_index + 1, p2_index + 1)
            winner = database.sorted_players[winner_index]
            print(f"Matchvinnare: {winner.name}\n" + 40*"=")

        # simulate match
        elif match_form == 2 or scorecard_choice == "ja":
            if scorecard_choice == "ja":
                selections = SelectionWindow(database.sorted_players)
                tk.mainloop()
                player1 = selections.player_selections[0]
                player2 = selections.player_selections[1]
                delay = float(selections.delay_selection)
                score_display = ScoreDisplay(player1, player2, database.sorted_players)

            match = Match(player1, player2, score_display)
            winner = match.simulate_match(delay, score_display, display_mode)
            print(f"Matchvinnare: {winner.name}\n" + 40*"=")

        # update stats
        winner.matches_won += 1
        player1.matches_played += 1
        player2.matches_played += 1

        # update file and show new list of players
        database.update_file()
        time.sleep(3)
        database.display_players()

        # decide wether to run program again or quit
        if scorecard_choice == "ja": # avslutar programmet efter 1 körning med gui 
            sys.exit()
        while True:
            try:
                choice_continue = input("\nVill du fortsätta? (ja/nej): ").lower().strip()
                if choice_continue == "ja":
                    break
                elif choice_continue == "nej":
                    sys.exit("Programmet avslutas.")
                else:
                    print('Felaktig inmatning. Skriv "ja" eller "nej"')
            except ValueError:
                print('Felaktig inmatning. Skriv "ja" eller "nej"')




if __name__ == "__main__":
    main()