#!/usr/bin/env python
__description__ = \
"""
Take output from qualtrics survey and generate a list of requested groups.

Students are given these instructions:
You may request up to three specific partners using [link to qualtrics
survey].  [For the student to log in, they must use their uoregon SSO, so this
validates the person making the request.  This SSO is then recorded in the 
survey results, so I know who made the request as a UO email address.]  
For a request to be valid, both people must request to be partners. 
(For example, if persons A and B want to be partners, person A must fill out
the form requesting B@uoregon.edu and person B must request A@uoregon.edu).  
If you submit the form more than once, I will only consider the last submission. 


This script is quite brittle at moment.  Assumes specific names/structure for
survey input.  Assumes 'email' column in class_list.
"""
__author__ = "Michael J. Harms"
__date__ = "2020-09-26"
__usage__ = "qualtrics_group_pref.py qualtrics_csv class_list_file"

import numpy as np
import pandas as pd

import copy, sys


def create_requested_groups(csv_file,class_list):
    """
    Load a qualtrics csv file of group requests. 
    """

    # Read data from data frame
    df = pd.read_csv(csv_file,header=1).iloc[1:]
   
    # Sanitize relevant columns
    requestors = []
    r1 = []
    r2 = []
    r3 = []
    for i in range(len(df["Recipient Email"])):
        requestors.append(str(df.iloc[i]["Recipient Email"]).strip().lower())
        r1.append(str(df.iloc[i]["Group member uoregon email address"]).strip().lower())
        r2.append(str(df.iloc[i]["Group member uoregon email address.1"]).strip().lower())
        r3.append(str(df.iloc[i]["Group member uoregon email address.2"]).strip().lower())


    # Create new df from cleaned up columns
    df = pd.DataFrame({"requestor":requestors,"r1":r1,"r2":r2,"r3":r3})

    # Sort from newest to oldest
    df = df.iloc[::-1]
 
    # Read the class list 
    if class_list[-4:] == ".csv":
        class_df = pd.read_csv(class_list)
    elif class_list[-4:] == "xlsx":
        class_df = pd.read_excel(class_list)        
    else:
        err = "class_list should be an excel or csv file\n"
        raise ValueError(err)
    
    # Grab email column    
    allowable_emails = class_df.email

    # Filter on allowable_emails
    df = df[df.requestor.isin(allowable_emails)]
    df.loc[np.logical_not(df.r1.isin(allowable_emails)),"r1"] = "None"
    df.loc[np.logical_not(df.r2.isin(allowable_emails)),"r2"] = "None"
    df.loc[np.logical_not(df.r3.isin(allowable_emails)),"r3"] = "None"

    # Make dict keyed to (email1,email2).  Value is number of times this key is
    # seen.  Key is sorted alphabetically by email. If only one party requests,
    # value will be one.  If both request, value will be two. 
    requestor_seen = {}
    request_dict = {}
    for i in range(len(df.requestor)):
        
        d = df.iloc[i]
        requestor = d.requestor

        # See if we have already seen this requestor.  If we have, move on (this
        # means we ignore any earlier requests from this requestor)
        try:
            requestor_seen[requestor]
            continue
        except KeyError:
            requestor_seen[requestor] = None

        # Go through requested partners...
        for r in [d.r1,d.r2,d.r3]:
            if r != "None":

                # Make a tuple of (email1,email2), sorted alphabetically for this
                # requestor/requestee pair
                request = [d.requestor,r]
                request.sort()
                request = tuple(request)

                # Record request
                try:
                    request_dict[request] += 1
                except KeyError:
                    request_dict[request] = 1
                
    # Now merge pairs
    groups = []
    for r in request_dict.keys():

        # If we got request from both people...
        if request_dict[r] == 2:
            
            merged = False
            new_pair = list(r)

            # Go through the existing groups
            for i, g in enumerate(groups):

                # If the new pair intersects one of the existing groups
                if len(g.intersection(new_pair)) > 0:

                    # Merge with the group and move on
                    new_group = new_pair
                    new_group.extend(list(g))
                    groups[i] = set(new_group)
                    merged = True
                    break
           
            # If we did not merge to an existing group, make a new one 
            if not merged:
                groups.append(set(new_pair))
                    
                    
    return groups
    
   
def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    try:
        survey_csv = argv[0]
        class_list = argv[1]
    except KeyError:
        err = f"Incorrect arguments. Usage:\n\n{__usage__}\n\n"
        raise ValueError(err)
   
    groups = create_requested_groups(survey_csv,class_list)

    return groups
  
if __name__ == "__main__":
    print(main())
   
    
