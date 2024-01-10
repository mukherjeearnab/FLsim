'''
Default Client Side Dataset Preprocessing Module
It absolutely does nothing to the train data, or the test data.
'''


def preprocess_dataset(train_tuple, test_tuple):
    '''
    Return the Train and Test datasets just the way it is.
    Different Variants might have data balancing processes for 
    Training and Testing datasets, like using SMOTE, or RandomUndersampling
    '''
    return train_tuple, test_tuple
