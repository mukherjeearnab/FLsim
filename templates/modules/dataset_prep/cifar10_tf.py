import tensorflow as tf


'''
Sample Dataset Preperation Module for MNSIT dataset
This module is executed before the client distribution 
for the dataset is performed in the Data Warehouse.
'''


def prepare_tf_dataset():
    '''
    Prepare the CIFAR10 Dataset here for Distribution to Clients
    NOTE: Returns the Train Set as the complete dataset.
    '''

    cifar10 = tf.keras.datasets.cifar10

    # Distribute it to train and test set
    (train_data, train_labels), (test_data, test_labels) = cifar10.load_data()
    print(train_data.shape, train_labels.shape,
          test_data.shape, test_labels.shape)

    train_data, test_data = train_data / 255.0, test_data / 255.0

    # return the tuple as ((train_data, train_labels), (test_data, test_labels)),
    # else if not test set, then ((train_data, train_labels), None)
    # on passing None, the server will split the train dataset into train and test, based on the train-test ratio
    return ((train_data, train_labels), (test_data, test_labels))
