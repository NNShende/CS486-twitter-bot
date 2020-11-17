import statistics
import matplotlib.pyplot as plt

# this file evaluates the tweets generated by the LSTM and GPT-2 models using the chrF (character n-gram F-score) algorithm

def chrF(real_text, generated_text):
    # print('real:', real_text)
    # print('gen:', generated_text)
    # print()
    generated_text_chars = set(generated_text)
    real_text_chars = set(real_text)
    precision = len([0 for c in generated_text if c in real_text_chars])    # fraction of n-grams present in the generated text that are also in the real text
    recall = len([0 for c in real_text if c in generated_text_chars])       # fraction of n-grams present in the real text that are also in the generated text
    if precision + recall == 0:
        return 0
    return 2*(precision * recall) / (precision + recall)

def wordF(real_text, generated_text):
    real_words = real_text.split()
    gen_words = generated_text.split()
    precision = len([0 for w in gen_words if w in real_words])    # fraction of n-grams present in the generated text that are also in the real text
    recall = len([0 for w in real_words if w in gen_words])    # fraction of n-grams present in the generated text that are also in the real text
    if precision + recall == 0:
        return 0
    return 2*(precision * recall) / (precision + recall)
    

ACTUAL_TRUMP_TWEETS_FILE_NAME = '../data/preprocessed_trump_test_data_filtered_for_LSTM'
ACTUAL_NEWS_TWEETS_FILE_NAME = '../data/test_news_data_filtered_for_LSTM'

GPT2_TRUMP_OUTPUT_FILE_NAME = '../GPT-2/trump_output'
GPT2_NEWS_OUTPUT_FILE_NAME = '../GPT-2/news_output'

LSTM_TRUMP_OUTPUT_FILE_NAME = '../LSTM/test-outputs/LSTM_trump_test_output'
LSTM_NEWS_OUTPUT_FILE_NAME = '../LSTM/test-outputs/LSTM_news_test_output'

# LSTM_TRUMP_OUTPUT_FILE_NAME = '../LSTM/test-outputs/trump-for-different-temperatures/output-0.2.txt'
# LSTM_NEWS_OUTPUT_FILE_NAME = '../LSTM/test-outputs/LSTM_news_test_output'

trump_set = (ACTUAL_TRUMP_TWEETS_FILE_NAME, GPT2_TRUMP_OUTPUT_FILE_NAME, LSTM_TRUMP_OUTPUT_FILE_NAME, 'Trump')
news_set = (ACTUAL_NEWS_TWEETS_FILE_NAME, GPT2_NEWS_OUTPUT_FILE_NAME, LSTM_NEWS_OUTPUT_FILE_NAME, 'News')

def get_lstm_graphs():
    temperatures = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2]
    avg_chrF_scores = []
    avg_wordF_scores = []
    with open(ACTUAL_TRUMP_TWEETS_FILE_NAME) as f:
        # real_lines = [l[:-1] for l in real_file.read().split('\n') if not l.isspace()]
        real_lines = [l[:-1].lower() for l in f.read().split('\n') if l.strip() != '']
    for temperature in temperatures:
        with open(f'../LSTM/test-outputs/trump-for-different-temperatures/output-{temperature}.txt') as f:
            lstm_lines = [l[:-1].lower() for l in f.read().split('\n') if l.strip() != '']
        chrF_scores = []
        wordF_scores = []
        for i in range(len(real_lines)):
            sixth_word_start_index = sum([len(w) for w in real_lines[i].split()[:5]]) + 4 # 4 spaces
            real_tweet, lstm_tweet = real_lines[i][sixth_word_start_index:], lstm_lines[i][sixth_word_start_index:]
            chrF_scores.append(chrF(real_tweet, lstm_tweet))
            wordF_scores.append(wordF(real_tweet, lstm_tweet))
        avg_chrF_scores.append(sum(chrF_scores)/len(chrF_scores))
        avg_wordF_scores.append(sum(wordF_scores)/len(wordF_scores))
    # plot
    fig1, ax1 = plt.subplots()
    ax1.plot(temperatures, avg_chrF_scores)
    ax1.set_title('LSTM: Temperature vs chrF')
    ax1.set_xlabel('Temperature')
    ax1.set_ylabel('chrF score')
    fig1.savefig('LSTM-temperature-vs-chrF.png')


    fig2, ax2 = plt.subplots()
    ax2.plot(temperatures, avg_wordF_scores)
    ax2.set_title('LSTM: Temperature vs wordF')
    ax2.set_xlabel('Temperature')
    ax2.set_ylabel('wordF score')
    fig2.savefig('LSTM-temperature-vs-wordF.png')


get_lstm_graphs()

for real_file, gpt_file, lstm_file, tweet_user in (trump_set, news_set):
    print('\n' + tweet_user)
    with open(real_file) as f:
        # real_lines = [l[:-1] for l in real_file.read().split('\n') if not l.isspace()]
        real_lines = [l[:-1].lower() for l in f.read().split('\n') if l.strip() != '']
    with open(lstm_file) as f:
        lstm_lines = [l[:-1].lower() for l in f.read().split('\n') if l.strip() != '']
    with open(gpt_file) as f:
        gpt_lines = [l[:-1].lower() for l in f.read().split('\n') if l.strip() != '']
    
    gpt_chrF_scores, lstm_chrF_scores = [], []
    gpt_wordF_scores, lstm_wordF_scores = [], []
    for i in range(len(real_lines)):
        sixth_word_start_index = sum([len(w) for w in real_lines[i].split()[:5]]) + 4 # 4 spaces
        min_len = min(len(real_lines[i]), len(lstm_lines[i]), len(gpt_lines[i]))
        real_tweet, lstm_tweet, gpt_tweet = real_lines[i][sixth_word_start_index:min_len], lstm_lines[i][sixth_word_start_index:min_len], gpt_lines[i][sixth_word_start_index:min_len]
        gpt_chrF_scores.append(chrF(real_tweet, gpt_tweet))
        lstm_chrF_scores.append(chrF(real_tweet, lstm_tweet))
        gpt_wordF_scores.append(wordF(real_tweet, gpt_tweet))
        lstm_wordF_scores.append(wordF(real_tweet, lstm_tweet))

    gpt_avg_chrF = sum(gpt_chrF_scores) / len(gpt_chrF_scores)
    lstm_avg_chrF = sum(lstm_chrF_scores) / len(lstm_chrF_scores)
    print('LSTM chrF score:\t', lstm_avg_chrF, '\tstddev:', statistics.stdev(lstm_chrF_scores))
    print('GPT-2 chrF score:\t', gpt_avg_chrF, '\tstddev:', statistics.stdev(gpt_chrF_scores))
    
    gpt_avg_wordF = sum(gpt_wordF_scores) / len(gpt_wordF_scores)
    lstm_avg_wordF = sum(lstm_wordF_scores) / len(lstm_wordF_scores)
    print('LSTM wordF score:\t', lstm_avg_wordF, '\tstddev:', statistics.stdev(lstm_wordF_scores))
    print('GPT-2 wordF score:\t', gpt_avg_wordF, '\tstddev:', statistics.stdev(gpt_wordF_scores))

