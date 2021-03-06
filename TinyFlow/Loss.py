import numpy as np


# Common loss class for regularization
class Loss:

    # Regularization loss calculation
    def regularization_loss(self, layer):

        # 0 by default
        regularization_loss = 0

        # L1 regularization - weights
        # Only calculate when factor greater than 0
        if layer.weight_regularizer_l1 > 0:
            regularization_loss += layer.weight_regularizer_l1 * \
                np.sum(np.abs(layer.weights))

        # L2 regularization - weights
        # Only calculate when factor greater than 0
        if layer.weight_regularizer_l2 > 0:
            regularization_loss += layer.weight_regularizer_l2 * \
                np.sum(layer.weights * layer.weights)

        # L1 regularization - biases
        # Only calculate when factor greater than 0
        if layer.bias_regularizer_l1 > 0:
            regularization_loss += layer.bias_regularizer_l1 * \
                np.sum(np.abs(layer.biases))

        # L2 regularization - biases
        # Only calculate when factor greater than 0
        if layer.bias_regularizer_l2 > 0:
            regularization_loss += layer.bias_regularizer_l2 * \
                np.sum(layer.biases * layer.biases)

        return regularization_loss

    # Regularization loss calculation

    def network_regularization_loss(self):
        '''network_regularization_loss (self)\n
            Internal method for network wrapper for auto calculation 
            of regularization loss of all the trainable layers
        '''

        # 0 by default
        regularization_loss = 0

        # Calculate regularization loss - iterate over all trainable layers
        for layer in self.trainable_layers:
            # L1 regularization - weights
            # Only calculate when factor greater than 0
            if layer.weight_regularizer_l1 > 0:
                regularization_loss += layer.weight_regularizer_l1 * \
                    np.sum(np.abs(layer.weights))

            # L2 regularization - weights
            # Only calculate when factor greater than 0
            if layer.weight_regularizer_l2 > 0:
                regularization_loss += layer.weight_regularizer_l2 * \
                    np.sum(layer.weights * layer.weights)

            # L1 regularization - biases
            # Only calculate when factor greater than 0
            if layer.bias_regularizer_l1 > 0:
                regularization_loss += layer.bias_regularizer_l1 * \
                    np.sum(np.abs(layer.biases))

            # L2 regularization - biases
            # Only calculate when factor greater than 0
            if layer.bias_regularizer_l2 > 0:
                regularization_loss += layer.bias_regularizer_l2 * \
                    np.sum(layer.biases * layer.biases)

        return regularization_loss

    # Set/remember trainable layers
    def remember_trainable_layers(self, trainable_layers):
        '''remember_trainable_layers (self, trainable_layers)\n
            internal method for Network wrapper to keep track of trainable layers
        '''

        self.trainable_layers = trainable_layers

    # Calculates the data and regularization losses
    # given model output and ground truth values

    def calculate(self, output, y, *, include_regularization=False):
        '''calculate(self, output, ground_truth)\n
            internal method for Network wrapper\n
            Calculates the data and regularization losses
            given model output and ground truth values
        '''

        # Calculate sample losses
        sample_losses = self.forward(output, y)

        # Calculate the mean loss
        data_loss = np.mean(sample_losses)

        # If just data loss is needed, return it
        if not include_regularization:
            return data_loss

        # Return the data and regularization losses
        return data_loss, self.network_regularization_loss()


# Cross-entropy loss
class Loss_CategoricalCrossEntropy(Loss):

    # Forward Pass
    def forward(self, y_pred, y_true):
        '''Loss_CategoricalCrossEntropy.forward (predicted_values, ground_truth)\n
            Returns the negative_log_likelihood for the correct class score.\n
            The loss returned is the mean loss over the batch.
        '''

        # Number of samples in a batch
        samples = y_pred.shape[0]

        # Probabilities for target values -
        # only if categorical labels
        if len(y_true.shape) == 1:
            y_pred = y_pred[range(samples), y_true]

        # Losses
        negative_log_likelihoods = -np.log(y_pred)

        # Mask values - only for one-hot encoded labels
        if len(y_true.shape) == 2:
            negative_log_likelihoods *= y_true

        # Overall loss
        data_loss = np.sum(negative_log_likelihoods) / samples

        return data_loss

    # Backward pass
    def backward(self, dvalues, y_true):
        '''Loss_CategoricalCrossEntropy.backward (upstream_gradient, labels)\n
        Calculates the backward pass for the current loss function\n
        ---IMPLEMENTATION TO BE UPDATED SOON---'''

        samples = dvalues.shape[0]

        # Make a backup so we can safely modify
        self.dvalues = dvalues.copy()
        self.dvalues[range(samples), y_true] -= 1
        self.dvalues = self.dvalues / samples


# Binary Cross-entropy loss
class Loss_BinaryCrossEntropy(Loss):

    # Forward Pass
    def forward(self, y_pred, y_true):

        # Clip data to prevent division by 0 (log(1) gives you 0)
        # Clip both sides to prevent any shifting the mean towards any value
        y_pred_clipped = np.clip(y_pred, 1e-7, 1 - 1e-7)

        # Calculate sample-wise loss
        sample_losses = -(y_true * np.log(y_pred_clipped) +
                          (1 - y_true) * np.log(1 - y_pred_clipped))

        #  Return losses
        return sample_losses

    # Backward pass
    def backward(self, dvalues, y_true):

        # Clip data to prevent division by 0 (log(1) gives you 0)
        # Clip both sides to prevent any shifting the mean towards any value
        clipped_dvalues = np.clip(dvalues, 1e-7, 1 - 1e-7)

        # Gradient on clipped values
        self.dvalues = -(y_true / clipped_dvalues -
                         (1 - y_true) / (1 - clipped_dvalues))


class Loss_MeanSquaredError(Loss):

    # Forward pass
    def forward(self, y_pred, y_true):

        # Calculate loss
        data_loss = 2 * np.mean((y_true - y_pred)**2, axis=-1)

        # return losses
        return data_loss

    # Backward pass
    def backward(self, dvalues, y_true):

        # Gradient on values
        self.dvalues = -(y_true - dvalues)
