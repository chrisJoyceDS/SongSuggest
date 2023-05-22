import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, recall_score, precision_score, f1_score)
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (AdaBoostClassifier, BaggingClassifier,
RandomForestClassifier)


# Model dictionary containing the different elements 
model_dict = {
              'rfc': # 1st level 2nd key
              
              {'model': # 2nd level 1st key
               
               ('rfc', RandomForestClassifier()),
               
               'params':# 2nd level 2nd key
               
               {"rfc__n_estimators": np.linspace(start = 200, stop = 2000, num = 10, dtype=int),
                "rfc__max_features": ['sqrt','log2', None],
                "rfc__max_depth": np.linspace(10, 110, num = 11, dtype=int),
                "rfc__min_samples_leaf": [1, 2, 4, 6, 8],
                "rfc__min_samples_split": [3, 5, 7, 10]}},
              
              'logreg': # 1st level 3rd key
              
              {'model': # 2nd level 1st key
               
               ('logreg', LogisticRegression()),
               
               'params':# 2nd level 2nd key
               
               {
                'logreg__C': np.logspace(-3, 3, 7),
                'logreg__solver': ['saga'],
                'logreg__max_iter': np.linspace(50, 50, 50)
              }},
              
              'abc': # 1st level 3rd key
              
              {'model': # 2nd level 1st key
               
               ('abc', AdaBoostClassifier()),
               
               'params':# 2nd level 2nd key
               
               {'abc__base_estimator': [DecisionTreeClassifier(), SVC(), RandomForestClassifier()],
                'abc__learning_rate': np.logspace(-3,0,4),
                'abc__n_estimators': np.linspace(start=50, stop=200, num=16, dtype=int)
              }},
              
              'bgc': # 1st level 3rd key
              
              {'model': # 2nd level 1st key
               
               ('bgc', BaggingClassifier()),
               
               'params':# 2nd level 2nd key
               
               {'bgc__base_estimator': [DecisionTreeClassifier(), SVC(), RandomForestClassifier()],
                'bgc__max_samples': np.linspace(0.1, 1.0, 10),
                'bgc__max_features': np.linspace(0.1, 1.0, 10),
                'bgc__n_estimators': np.linspace(start=50, stop=200, num=16, dtype=int)
              }},
              
              'svc': # 1st level 3rd key
              
              {'model': # 2nd level 1st key
               
               ('svc', SVC()),
               
               'params':# 2nd level 2nd key
               
               {'svc__C': np.logspace(-3, 3, 7),
                'svc__kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
                'svc__gamma': np.logspace(-5, 0, 6)
              }}
             
             
             }




def get_best_models(X_train, y_train):
    """
    This function takes in only two parameters: X_train and y_train. The function is designed to find the best estimators and params for the different models selected in the model dictionary and return them for scoring. 
    
    The function loops through the model dictionary instantiating a new pipeline per iteration that by default includes CountVectorizer to prepare the tokenized and stemmed data for GridSearchCV. Each iteration appends a different estimator to the pipeline to be passed into GridSearchCV with its own specified hyper params.
    
    After each fit is concluded, it saves a dictionary with the key associated to the model type and the values of: best_estimator_, best_params_, and pipe.
    """
    
    # set dictionary to house best estimators and params
    best_models = {}
    # for loop through the 3 1st level keys of model_model dict
    for key, value in model_dict.items():
        # set pipeline with current iteration
        pipe = Pipeline([value['model']])
        print(pipe)
        rs = RandomizedSearchCV(pipe,# current pipe iteration
                                value['params'], # current params iteration
                                cv=5, # cross validation 5
                                random_state=42, # random state for consistent results
                                n_jobs=-1) # unlock available CPU for processing
        # fit the current iteration of RandomizedSearchCV
        rs.fit(X_train, y_train)
        # save the best model, best params, and the pipe for scoring 
        best_models[key] = {'model': rs.best_estimator_,
                            'params': rs.best_params_}
    return best_models


def record_scores(baseline, X_train, y_train, X_test, y_test, best_models, model_name:str, df_scores=None):
    """
    This function was originally designed by Devin Fay, instructor for DSIR-221 to capture the scores of multiple model iterations in a dataframe. I have taken out the confusion matrix display and added a couple of different lines, but want to give credit where credit is due.
    
    Changes I made were:
    1. Pass the baseline model for reference
    2. Created a version column and model_type column to keep track of times run
    3. Iteration over a dictionary of best estimators
    """
    if df_scores is None:
        df_scores = pd.DataFrame(columns = ['version','baseline','model_type','train_acc', 'test_acc', 'bal_acc', 'recall', 'precision', 'f1_score'])
    # version equals length of df_scores divided by number of models (6 here)
    version = 'v' + (str((len(df_scores)//5)+1))
        
    # iterate through best_models dictionary
    for model, model_dict in best_models.items():
        # set type
        model_type = model
        # per model, fit the RandomizedSearchCV best_estimator_
        model_dict['model'].fit(X_train, y_train)
        # create predictions
        preds = model_dict['model'].predict(X_test)
        # score accuracy for training data
        train_acc = model_dict['model'].score(X_train, y_train)
        # score accuracy for test data
        test_acc = model_dict['model'].score(X_test, y_test)
        # score balanced accuracy
        bal_acc = balanced_accuracy_score(y_test, preds)
        # calculate recall (TP/(TP+FN))
        rec = recall_score(y_test, preds)
        # calculate precision (TP/(TP+FP))
        prec = precision_score(y_test, preds)
        # calculate F1, ratio of Precision and recall
        fone = f1_score(y_test, preds)
        # create row identifier
        model_name_df = model_name + '_' + model
        # create row for model
        df_scores.loc[model_name_df,:] = [version, baseline, model_type, train_acc, test_acc, bal_acc, rec, prec, fone]

    return df_scores
