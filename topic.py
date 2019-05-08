from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
from gensim.parsing.preprocessing import remove_stopwords
from gensim.models import CoherenceModel
import matplotlib.pyplot as plt
import numpy as np


def print_top_words(model, feature_names, n_top_words):
    """print top words for sk-learn methods"""
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()


def idf_list(filename, n):
    """construct a list with top n idf words"""
    idf = []
    with open(filename, 'r') as file:
        for line in file:
            line_1 = line.strip('\n')
            idf.append(line_1.split(' ')[0])
    return idf[:n-1]


def list_inter(list_1, list_2):
    """find the elements in lise_1 not in list_2"""
    return [a for a in list_1 if a not in list_2 and len(a) > 1]


def process_doc(filename_1, top_idf_number):
    """preprocess document"""
    file_1 = filename_1.split("/")
    if len(file_1) == 1:
        idf_file_1 = "idf/idf"+file_1[0]
        filename_1 = "word/word" + file_1[0]
    else:
        idf_file_1 = "idf/" + file_1[0]+"/idf" + file_1[1]
        filename_1 = "word/" + file_1[0]+"/word" + file_1[1]
    idf_1 = idf_list(idf_file_1, top_idf_number)
    common_texts = []
    with open(filename_1, 'r') as file:
        for line in file:
            line_1 = line.strip('\n')
            line_1 = remove_stopwords(line_1)
            if line_1.split(' ')[-1] == "":
                common_texts.append(list_inter(line_1.split(' ')[:-1], idf_1))
            else:
                common_texts.append(list_inter(line_1.split(' '), idf_1))
    return common_texts


def optimal_topic_number(filename_1, top_idf_number):
    """how to find the optimal number of topics using coherence score."""
    common_texts = process_doc(filename_1, top_idf_number)
    common_dictionary = Dictionary(common_texts)
    common_corpus = [common_dictionary.doc2bow(text) for text in common_texts]
    coherence_score = []
    for i in range(20, 40):
        lda = LdaModel(common_corpus, id2word=common_dictionary, iterations=50, num_topics=i)
        coherence_model_lda = CoherenceModel(model=lda, texts=common_texts, dictionary=common_dictionary,
                                             coherence='u_mass')
        coherence_lda = coherence_model_lda.get_coherence()
        print('\nCoherence Score: ', coherence_lda)
        coherence_score.append(coherence_lda)
    plt.plot(range(20, 40, 1), coherence_score)
    plt.xlabel("Num Topics")
    plt.ylabel("Coherence score")
    plt.legend("coherence_values", loc='best')
    plt.show()


def topic_classification_gensim_train(filename_1, topic_number, top_idf_number):
    """use gensim to perform lda algorithm"""
    common_texts = process_doc(filename_1, top_idf_number)
    common_dictionary = Dictionary(common_texts)
    common_corpus = [common_dictionary.doc2bow(text) for text in common_texts]
    lda = LdaModel(common_corpus, id2word=common_dictionary, iterations=50, num_topics=topic_number)
    for index, topic in lda.show_topics(formatted=False, num_words=20, num_topics=topic_number):
        print('Topic: {} \nWords: {}'.format(index, [w[0] for w in topic]))
    # print the topic and words
    topic_2 = [0.00 for n in range(topic_number)]
    for seen_doc in common_corpus:
        vector_1 = lda[seen_doc]
        for vec in vector_1:
            topic_2[vec[0]] = topic_2[vec[0]]+vec[1]
        # find the distribution of each topic.
    topic_2 = np.array(topic_2) / np.linalg.norm(topic_2)
    print(filename_1+" word distribution:")
    print(topic_2)
    return topic_2, lda, common_dictionary


def topic_classification_gensim_fit(filename_2, topic_number, top_idf_number, lda_model, common_dictionary):
    topic_1 = [0.00 for n in range(topic_number)]
    common_texts = process_doc(filename_2, top_idf_number)
    common_corpus = [common_dictionary.doc2bow(text) for text in common_texts]
    for unseen_doc in common_corpus:
        vector = lda_model[unseen_doc]
        for vec in vector:
            topic_1[vec[0]] = topic_1[vec[0]]+vec[1]
    topic_1 = np.array(topic_1)/np.linalg.norm(topic_1)
    print(filename_2 + " word distribution:")
    print(topic_1)
    return topic_1


def topic_classification(filename):
    """Use sk-learn to perform lda algorithm"""
    corpus = []
    with open(filename, 'r') as file:
        for line in file:
            corpus.append(line.strip('\n'))
    vectorizer = CountVectorizer(stop_words='english', max_df=0.2, min_df=0.1)
    cntTf = vectorizer.fit_transform(corpus)
    lda = LatentDirichletAllocation(n_components=30,
                                    learning_method='batch',
                                    learning_offset=50.,
                                    random_state=0)
    lda.fit(cntTf)
    tf_feature_names = vectorizer.get_feature_names()
    print_top_words(lda, tf_feature_names, 6)


def plot_scatter(topic_1, topic_2, topic_number):
    ax = plt.subplot()
    ax.scatter(range(0, topic_number), topic_1, c='red', alpha=0.6)
    ax.scatter(range(0, topic_number), topic_2, c='green', alpha=0.6)
    plt.show()


def main():
    # topic_classification('word90-92.txt')
    # optimal_topic_number('11-13.txt', 50)
    topic_2, lda, dictionary = topic_classification_gensim_train('11-13.txt', 35, 30)
    file = ['Information_retrieval/11-13.txt', 'Computer_vision/11-13.txt']
    for i in file:
        topic_classification_gensim_fit(i, 35, 30, lda, dictionary)


if __name__ == '__main__':
    main()
