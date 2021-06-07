
def check_unique(col, df, dropna=False):
    
    """Takes in a Pandas DataFrame and specific column name and returns a Pandas DataFrame 
    displaying the unique values in that column as well as the count of each unique value. 
    Default is to also provide a count of NaN values.
    
    Args:
        col (str): Name of the column you want to check.
        df (Pandas DataFrame): DataFrame containing the column to check the unique values of.
        dropna (bool, default=False): Whether or not to drop null values from list of values.
    
    Returns:
        DataFrame: Pandas DataFrame with columns for the unique values in the specified column, 
            the number of occurrences of each unique value in that column, and the percentage of 
            the column made up by each unique value.
    
    Example:
        >>> df = pd.DataFrame({'a': [2, 4, 4, 6],
                               'b': [2, 1, 3, 4]})
        >>> check_unique(col='a', df, dropna=False)
        
            count   %
        4   2   0.50
        6   1   0.25
        2   1   0.25
    """
    
    import pandas as pd
    
    unique_vals = pd.DataFrame()
    unique_vals['count'] = pd.Series(df[col].value_counts(dropna=dropna))
    unique_vals['%'] = pd.Series(round(df[col].value_counts(normalize=True, dropna=dropna)*100, 2))
    
    display(unique_vals.style.set_caption(col))


#################################################################################
#################################################################################

#################################################################################
#################################################################################



## Print out token info and descriptions for a spacy doc 
def token_report(doc, tags=False):
    
    if tags:
        dash_multi = 32
    else:
        dash_multi =15
    
    print('---'*dash_multi)
    print('---'*dash_multi)
    if tags:
        print(f'{"Token":{12}} {"Lemma":{12}} {"POS":{8}} {"Dependency":{12}} {"Tag":{6}} {"Tag Explanation":{24}}')
    else:
        print(f'{"Token":{12}} {"Lemma":{12}} {"POS":{8}} {"Dependency":{12}}')
    print('---'*dash_multi)
    for token in doc:
        if tags:
            print(f'{token.text:{12}} {token.lemma_:{12}} {token.pos_:{8}} {token.dep_:{12}} {token.tag_:{6}} {spacy.explain(token.tag_):{24}}')
        else:
            print(f'{token.text:{12}} {token.lemma_:{12}} {token.pos_:{8}} {token.dep_:{12}}')
    print('---'*dash_multi)

