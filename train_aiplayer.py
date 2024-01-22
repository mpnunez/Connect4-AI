from connect4lib.game import Game
from connect4lib.player import RandomPlayer, ColumnSpammer
from connect4lib.aiplayer import AIPlayer
from tqdm import tqdm
import numpy as np
from keras.models import load_model

def play_matches(trainee, opponents, n_games=100):
    all_move_records = []
    trainee_wlt_record = np.zeros([len(opponents),3],dtype=int)
    WIN = 0
    LOSS = 1
    TIE = 2
    
    for i in tqdm(range(n_games)):
        #print(f"{i}/{n_training_games}")
        
        opponent_ind = (i//2)%len(opponents)    # Play each opponent twice in a row
        opponent = opponents[opponent_ind]
        trainee_position = i%2
        opponent_position = (trainee_position+1)%2
        
        g = Game()
        g.players = [None,None]
        g.players[trainee_position] = trainee        # Alternate being player 1/2
        g.players[opponent_position] = opponent   
        
        
        winner, records = g.play_game()
        all_move_records += records
        
        if winner == -1:
            trainee_wlt_record[opponent_ind,TIE] += 1
        elif winner == trainee_position:
            trainee_wlt_record[opponent_ind,WIN] += 1
        else:
            trainee_wlt_record[opponent_ind,LOSS] += 1

        
    return all_move_records, trainee_wlt_record
        

def main():
    
    magnus = AIPlayer(name="Magnus")
    random_bot = RandomPlayer("Random Bot")
    opponents = [random_bot, ColumnSpammer(name="ColumnSpammer",randomness_weight=0.2)]
    
    n_training_rounds = 10
    for training_round in range(n_training_rounds):
    
        trainee = random_bot if training_round == 0 else magnus    # Use random bot in 1st round to save time 
        all_move_records, win_loss_ties = play_matches(trainee, opponents, n_games=100)

        # Print table of win/loss/tie/records
        print("Opponent\tWins\tLosses\tTies")
        for op, row in zip(opponents,win_loss_ties):
            print(f"{op.name}\t",end='')
            for col in row:
                print(f"{col}\t",end='')
            print()
            
        winning_move_records = [mr for mr in all_move_records if mr.result == 1]
        magnus.train_on_game_data(winning_move_records)
        chkpt_fname = f'magnus-{training_round}.h5'
        magnus.model.save(chkpt_fname)
        
        # Add copy of self to opponent list
        magnus_clone = AIPlayer(name=f"Magnus-{training_round}",randomness_weight=0.2)
        magnus_clone.model = load_model(chkpt_fname)
        opponents.append(magnus_clone)

if __name__ == "__main__":
    main()

