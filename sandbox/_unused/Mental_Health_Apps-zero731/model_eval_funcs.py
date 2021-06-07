def eval_classifier(clf, X_test, y_test, model_descr='',
                    target_labels=['neg', 'pos'],
                    cmap='Blues', normalize='true', save=False, fig_name=None):
    
    """Given an sklearn classification model (already fit to training data), test features, and test labels,
       displays sklearn.metrics classification report and confusion matrix. A description of the model 
       can be provided to model_descr to customize the title of the classification report.
       
       
    Args:
        clf (estimator): Fitted classifier.
        X_test (series or array): Subset of X data used for testing.
        y_test (series or array): Subset of y data used for testing.
        model_descr (str): A description of the model for customizing plot title.
        target_labels (list of strings, default=['Early', 'Election Day', 'No Vote']): List of class labels 
            used for formatting tick labels.
        cmap (str, default='Blues'): Specifies a color map that can be used by sklearn's plot_confusion_matrix.
        normalize (str, {'true', 'pred', 'all', None}, default='true'): Whether to normalize the
        confusion matrix over the true (rows), predicted (columns) conditions or all the population. 
        If None, confusion matrix will not be normalized.
        save (bool, default=False): Whether to save the returned figure.
        fig_name (str, optional): What to name the file if the image is being saved.
    
    Returns:
        display: Sklearn classification report and confusion matrix.
    
    Example:
        >>> eval_classifier(clf=my_model, X_test, y_test, model_descr='My Model',
                    target_labels=['neg', 'pos'],
                    cmap='Blues', normalize='true', save=true, fig_name='my_model_eval')
    
    """
    
    import matplotlib.pyplot as plt
    from sklearn.metrics import classification_report, plot_confusion_matrix
    
    
    fig_filepath = 'Figures/'
    
    ## get model predictions
    y_hat_test = clf.predict(X_test)
    
    
    ## Classification Report
    report_title = 'Classification Report: {}'.format(model_descr)
    divider = ('-----' * 11) + ('-' * (len(model_descr) - 31))
    report_table = classification_report(y_test, y_hat_test,
                                         target_names=target_labels)
    print(divider, report_title, divider, report_table, divider, divider, '\n', sep='\n')
    
    
    ## Make Subplots for Figures
    fig, axes = plt.subplots(figsize=(10,6))
    
    ## Confusion Matrix
    plot_confusion_matrix(clf, X_test, y_test, 
                          display_labels=target_labels, 
                          normalize=normalize, cmap=cmap, ax=axes)
    
    axes.set_title('Confusion Matrix:\n{}'.format(model_descr),
                   fontdict={'fontsize': 18,'fontweight': 'bold'})
    axes.set_xlabel(axes.get_xlabel(),
                       fontdict={'fontsize': 12,'fontweight': 'bold'})
    axes.set_ylabel(axes.get_ylabel(),
                       fontdict={'fontsize': 12,'fontweight': 'bold'})
    axes.set_xticklabels(axes.get_xticklabels(),
                       fontdict={'fontsize': 10,'fontweight': 'bold'})
    axes.set_yticklabels(axes.get_yticklabels(), 
                       fontdict={'fontsize': 10,'fontweight': 'bold'})
    
    
    if save:
        plt.savefig(fig_filepath+fig_name, bbox_inches = "tight")
    
    fig.tight_layout()
    plt.show()

    return fig, axes



#################################################################################
#################################################################################

#################################################################################
#################################################################################