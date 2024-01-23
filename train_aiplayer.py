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
    #magnus.random_weight = 0.1
    random_bot = RandomPlayer("Random Bot")
    #opponents = [random_bot, ColumnSpammer(name="ColumnSpammer")]
    #opponents = [ColumnSpammer(name=f"ColumnSpammer-{i}",col_preference=i) for i in range(7)]
    # opponents = [ColumnSpammer(name=f"ColumnSpammer",col_preference=4)]
    opponents = [RandomPlayer(name=f"Random Bot")]
    self_play = False
    percentile_keep = 0.3       # Train on this fraction of best games
    SAVE_MODEL_EVERY_N_BATCHES = 100
    GAMES_PER_TRAINING_BATCH = 100

    n_training_rounds = 1000
    for training_round in range(n_training_rounds):
    
        all_move_records, win_loss_ties = play_matches(magnus, opponents, n_games=GAMES_PER_TRAINING_BATCH)

        # Print table of win/loss/tie/records
        print("Opponent\tWins\tLosses\tTies")
        for op, row in zip(opponents,win_loss_ties):
            print(f"{op.name}\t",end='')
            for col in row:
                print(f"{col}\t",end='')
            print()
            
        agent_move_records = [mr for mr in all_move_records if mr.player_name == "Magnus"]
        if len(agent_move_records) == 0:
            continue
        agent_move_records = sorted(agent_move_records)
        records_to_train = int(len(agent_move_records)*percentile_keep)
        move_records_for_training = [mr for mr in agent_move_records[-records_to_train:]]

        magnus.train_on_game_data(move_records_for_training)
        if training_round % SAVE_MODEL_EVERY_N_BATCHES == 0:
            chkpt_fname = f'magnus-{training_round}.h5'
            magnus.model.save(chkpt_fname)
        
        if self_play:
            # Add copy of self to opponent list
            magnus_clone = AIPlayer(name=f"Magnus-{training_round}",randomness_weight=0.2)
            magnus_clone.model = load_model(chkpt_fname)
            opponents.append(magnus_clone)

if __name__ == "__main__":
    main()
