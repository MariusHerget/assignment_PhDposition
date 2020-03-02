#!/usr/bin/env python
# coding: utf-8

# # Task 4
# ## Assignment for PhD positions in computational social sciences here at ETH Züric
# 
# ### by Marius Herget
# 
# 
# 
# 
# #### Step 1
# Import all necessary packages and datasets. (including creationg of some helper functions)
# 

# In[1]:


import pandas as pd
import scipy as scipy
import networkx as nx
import matplotlib.pyplot as plt
import requests


# In[2]:


# Helper functions
def normalize(df, column_name):
    result = df.copy()
    max_value = df[column_name].max()
    min_value = df[column_name].min()
    result[column_name+"_normalized"] = (df[column_name] - min_value) / (max_value - min_value)
    return result
def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x.to_markdown())
    pd.reset_option('display.max_rows')


# In[3]:


# Import data provided by github
adjax_matices = pd.read_csv("./task4_data/adjacency_matrices-115.csv",sep="\t", index_col=0, header=0)
adjax_matices.columns = adjax_matices.columns.astype('int64')
bills = pd.read_csv("./task4_data/bills-115.csv",sep="\t",header=0,index_col="bill_id")
edgelists = pd.read_csv("./task4_data/edgelists-115.csv",sep="\t",header=0,index_col=0)
individuals = pd.read_csv("./task4_data/individuals.csv",sep="\t",header=0,index_col="SGID")
members = pd.read_csv("./task4_data/members-115.csv",sep="\t",header=0,index_col="SGID")


# ##### *bills_in_better* 
# 
# This is a better version of the given _bills_ dataset: it was created by the code in step 4 and afterward saved in a file.
# 

# In[4]:


# Import extra data from generated data
bills_in_better = pd.read_csv("./extraData/better_bills.csv")


# ##### *individuals_money* 
# 
# This is a manipulated version of the given _individuals_ dataset: it was created by the code in step 3, modified in step 4, and afterward saved in a file to avoid unnecessary traffic.

# In[5]:


# Import extra data from generated data
individuals_money = pd.read_csv("./extraData/individuals_money.csv")


# #### Step 2
# Do some basic calculations on the dataset to understand it.

# In[6]:


# Basic analysis to understand the dataset
summedupMatrix_gived_signatures = adjax_matices.sum(axis=1,)
summedupMatrix_received_signatures = adjax_matices.sum(axis=0,)
index = summedupMatrix_received_signatures.idxmax()
 
print('The higehst number of given cosponsorships:')
print(summedupMatrix_gived_signatures.loc[index])
print('The higehst number of received cosponsorships:')
print(summedupMatrix_received_signatures.loc[index])


# #### Step 3
# ##### Importance of each representative
# 
# 
# As mentioned in my submission to calculate the importance of each representative, available/spent money is a crucial factor. Another factor is the popularity within the voting base, experience, and standing within the own party. Therefore, re-election is also considered within the evaluation.
# 
# This data is affected by step 4 as well. Hence we will load it from a csv as well (saving in step 4).

# ##### *follow_the_money*
# 
# This data is needed to calculate the importance of each representative.
# 
# Reference: *House Office Expenditure Data, propublica.org, visited: 24.02.2020, URL: https://projects.propublica.org/represent/expenditures*

# In[7]:


# Import extra from Congress 115 Money Spending
def load_follow_the_money():
    follow_the_money = pd.read_csv("./extraData/house-office-expenditures-with-readme/2017Q1-house-disburse-summary.csv")
    follow_the_money = follow_the_money.append(pd.read_csv("./extraData/house-office-expenditures-with-readme/2017Q2-house-disburse-summary.csv"), ignore_index = True, sort=False)
    follow_the_money = follow_the_money.append(pd.read_csv("./extraData/house-office-expenditures-with-readme/2017Q3-house-disburse-summary.csv"), ignore_index = True, sort=False)
    follow_the_money = follow_the_money.append(pd.read_csv("./extraData/house-office-expenditures-with-readme/2017Q4-house-disburse-summary.csv"), ignore_index = True, sort=False)
    follow_the_money = follow_the_money.append(pd.read_csv("./extraData/house-office-expenditures-with-readme/2018Q1-house-disburse-summary.csv"), ignore_index = True, sort=False)
    follow_the_money = follow_the_money.append(pd.read_csv("./extraData/house-office-expenditures-with-readme/2018Q2-house-disburse-summary.csv"), ignore_index = True, sort=False)
    follow_the_money = follow_the_money.append(pd.read_csv("./extraData/house-office-expenditures-with-readme/2018Q3-house-disburse-summary.csv"), ignore_index = True, sort=False)
    follow_the_money = follow_the_money.append(pd.read_csv("./extraData/house-office-expenditures-with-readme/2018Q4-house-disburse-summary.csv"), ignore_index = True, sort=False)
    follow_the_money = follow_the_money.append(pd.read_csv("./extraData/house-office-expenditures-with-readme/2019Q1-house-disburse-summary.csv"), ignore_index = True, sort=False)
    follow_the_money = follow_the_money.append(pd.read_csv("./extraData/house-office-expenditures-with-readme/2019Q2-house-disburse-summary.csv"), ignore_index = True, sort=False)
    follow_the_money = follow_the_money.append(pd.read_csv("./extraData/house-office-expenditures-with-readme/2019Q3-house-disburse-summary.csv"), ignore_index = True, sort=False)
    return follow_the_money


# In[8]:


def calculateImportanceRepresentative():
    # Representative importance
    follow_the_money = load_follow_the_money()
    follow_the_money["BIOGUIDE_ID"] = follow_the_money["BIOGUIDE_ID"].astype(str) 
    follow_the_money = follow_the_money.drop(columns="YEAR")
    follow_the_money = follow_the_money.drop(columns="YTD")
    follow_the_money = follow_the_money.groupby(['BIOGUIDE_ID']).sum()
    individuals_money = pd.merge(individuals,follow_the_money,left_on=["bioguide_id"], right_on = ['BIOGUIDE_ID'], how = 'left')
    # individuals_money => mapped data of representatives with money spending from 2017 Q1 to 2019 Q3
    individuals_money = normalize(individuals_money, "AMOUNT")
    individuals_money = normalize(individuals_money, "115_signatures_received")
    individuals_money = normalize(individuals_money, "115_signatures_given")

    # Consideration of re-elections
    individuals_money.loc[individuals_money["111"] == True, "in_congress_last_five_periods"] = 1
    individuals_money.loc[individuals_money["111"] == False, "in_congress_last_five_periods"] = 0
    individuals_money.loc[individuals_money["112"] == True, "in_congress_last_five_periods"] += 1
    individuals_money.loc[individuals_money["113"] == True, "in_congress_last_five_periods"] += 1
    individuals_money.loc[individuals_money["114"] == True, "in_congress_last_five_periods"] += 1
    individuals_money["in_congress_last_five_periods"] = individuals_money["in_congress_last_five_periods"]/4

    individuals_money["importance"] = individuals_money["AMOUNT_normalized"] * 0.5 
    individuals_money["importance"] += individuals_money["in_congress_last_five_periods"] * 0.5
    individuals_money["supported_D"] = 0
    individuals_money["supported_R"] = 0
    individuals_money["supported_OTHER"] = 0
    return individuals_money


# #### Step 4
# ##### Get some more information about each bills
# 
# ProPublica provides an exhausting interface for different information about the US government.  Fascinating is the fact that they show which cosponsors support each bill. Therefore, I save which party supports which bill and which senator supports how many bills from each party.
# 
# Reference: *Congress API, propublica.org, visited: 24.02.2020, URL: https://projects.propublica.org/api-docs/congress-api/bills/#get-cosponsors-for-a-specific-bill*

# In[9]:


# Import of interesting bill data 
individuals_money_TMP = calculateImportanceRepresentative()
progress = 0
errorbacklog = pd.DataFrame(["first"], columns=list('h'))

def getInterestingData(bill):
    global progress
    progress += 1
    if progress % 50 == 0 or progress == 1:
        print(progress)
    result = bill
    url = "https://api.propublica.org/congress/v1/115/bills/"+str(bill["bill_type"])+str(bill["bill_number"])+"/cosponsors.json"
    try:
        r = requests.get(url, headers = {"X-API-Key": "hGZo7tcTCDpenT7PvpVj2FudUvsMQG6w9nURbIGZ"})
        r.raise_for_status()
        if len(r.json()["results"]):
            if len(r.json()["results"]) > 0:
                for s in r.json()["results"][0]["cosponsors_by_party"]:  
                    result["cosponsors_by_party_"+s["party"]["id"]] = s["party"]["sponsors"]
                result["total_cosponser"] =  r.json()["results"][0]["number_of_cosponsors"]
                for s in r.json()["results"][0]["cosponsors"]:  
                    addVoteToRepresentative(s["cosponsor_id"], r.json()["results"][0]["sponsor_party"])
            else:
                print("No results for "+str(bill["bill_type"])+str(bill["bill_number"]))
        return result
    except requests.exceptions.HTTPError as err:
        errorbacklog = errorbacklog.append(pd.DataFrame([str(bill["bill_type"])+str(bill["bill_number"])], columns=list('h')))
        print(errorbacklog)
        print(err)
        
def addVoteToRepresentative(bioguide_id, party):
    switcher = {
        "D": "supported_D",
        "R": "supported_R",
    }
    pa = switcher.get(party, "supported_OTHER")
    individuals_money_tmp.loc[individuals_money["bioguide_id"] == bioguide_id, pa] += 1
    
### Comment this in if you want to reload all data from the external sources ###
#bills_better = bills[:]
#bills_better = bills_better.apply(lambda bill : getInterestingData(bill), axis=1) 
#print("done")
#bills_better.to_csv("./better_bills.csv")
#individuals_money_tmp.to_csv("./individuals_money.csv")
#individuals_money = individuals_money_tmp


# #### Step 5
# ##### Calculate importance of each bill
# 
# This step evaluates the importance of each bill. Details can be found in my submission.
# 
# General rules:
# The more opposite party member supported the bill the more important (+10%)
# The more same party members supported the bill the more important (-10%)

# In[10]:


# Bill importance
bills_in_better_tmp = pd.merge(bills_in_better,members[['party']],left_on=["sponsor_SGID"], right_index=True, how = 'left')
# Adjust naming
bills_in_better_tmp.loc[bills_in_better_tmp["party"] == "Republican", "party"] = "R"
bills_in_better_tmp.loc[bills_in_better_tmp["party"] == "Democrat", "party"] = "D"
bills_in_better_tmp["cosponsors_by_party_R"] = bills_in_better_tmp["cosponsors_by_party_R"].fillna(0.)
bills_in_better_tmp["cosponsors_by_party_D"] = bills_in_better_tmp["cosponsors_by_party_D"].fillna(0.)

# Normalize
bills_in_better_tmp = normalize(bills_in_better_tmp, "total_cosponser")

def setImportanceBill(bill):
    result = bill
    if bill["party"] == "R" or bill["party"] == "D":
        own_party_votes = bill["cosponsors_by_party_" + str(bill["party"])]
    else:
        own_party_votes = bill["total_cosponser"] - (bill["cosponsors_by_party_R"] + bill["cosponsors_by_party_D"])
    if bill["party"] == "R":
        other_party_votes = bill["cosponsors_by_party_D"]
    else:
        if bill["party"] == "D":
            other_party_votes = bill["cosponsors_by_party_R"]
        else:
            other_party_votes = (bill["cosponsors_by_party_R"] + bill["cosponsors_by_party_D"]) - bill["total_cosponser"]
    
    result["BillImportance"] =  1.1 * (float(other_party_votes)/float(bill["total_cosponser"]))
    result["BillImportance"] += 0.9 * (float(own_party_votes)  /float(bill["total_cosponser"]))
    result["BillImportance"] *= bill["total_cosponser_normalized"]
    return result

bills_in_better_tmp = bills_in_better_tmp.apply(lambda bill : setImportanceBill(bill), axis=1) 
bills_in_better_final = bills_in_better_tmp


# In[11]:


ten_most_important_bills = bills_in_better_final.nlargest(10, "BillImportance")
print('The ten most importance bills: ')
ten_most_important_bills


# #### Step 6
# ##### Combine all evaluated data
# 
# Merge the data sets to map bill importance and the information about the members to the members of the House of Representatives.
# 

# In[12]:


members_of_115_all = pd.merge(members.reset_index(),individuals_money[["115_signatures_received","115_signatures_given","bioguide_id","AMOUNT",'AMOUNT_normalized', '115_signatures_received_normalized','115_signatures_given_normalized','in_congress_last_five_periods','importance']],left_on=["bioguide_id"], right_on = ['bioguide_id'], how = 'left').set_index('SGID')
print("Representatives of the 10 most important bills:")
members_of_115_all.loc[ten_most_important_bills["sponsor_SGID"]]


# In[13]:


# Group bills by sponsor
bills_grouped_by_sponsor = bills_in_better_final.drop(columns="bill_id")
bills_grouped_by_sponsor = bills_grouped_by_sponsor.drop(columns="bill_number")
bills_grouped_by_sponsor = bills_grouped_by_sponsor.drop(columns="bill_type")
bills_grouped_by_sponsor = bills_grouped_by_sponsor.drop(columns="congress")
bills_grouped_by_sponsor = bills_grouped_by_sponsor.drop(columns="introduced_at")
bills_grouped_by_sponsor = bills_grouped_by_sponsor.drop(columns="total_cosponser_normalized")
bills_grouped_by_sponsor = bills_grouped_by_sponsor.groupby(['sponsor_SGID']).sum()
bills_grouped_by_sponsor = normalize(bills_grouped_by_sponsor, "BillImportance")


# In[18]:


# Combine all members and bills with most interesting informationen
members_with_all_information = pd.merge(members_of_115_all.reset_index(), bills_grouped_by_sponsor, left_on=["SGID"], right_index=True, how = 'left').set_index('SGID')
# Filter members with no own bill or 0 own importance
deleteindex = members_with_all_information[(pd.notna(members_with_all_information["BillImportance"])) & members_with_all_information["importance"] == 0.].index
members_with_all_information = members_with_all_information.drop(deleteindex)
# Calculate overall Importance
def calculateOverAllImportance(m):
    result = m
    result["overallImportance"] = 0.5 * m["importance"] + 0.5 * m ["BillImportance_normalized"]
    return result

members_with_all_information = members_with_all_information.apply(lambda bill : calculateOverAllImportance(bill), axis=1) 
members_with_all_information.nlargest(10, "overallImportance").columns


# In[38]:


# Export for Submission
latex_export = members_with_all_information.nlargest(10, "overallImportance")
latex_export = latex_export.drop(columns="thomas_id")
latex_export = latex_export.drop(columns="state")
latex_export = latex_export.drop(columns="bioguide_id")
latex_export = latex_export.drop(columns="congress")
latex_export = latex_export.drop(columns="115_signatures_received_normalized")
latex_export = latex_export.drop(columns="115_signatures_given_normalized")
latex_export = latex_export.drop(columns="total_cosponser")
latex_export = latex_export.drop(columns="BillImportance_normalized")
latex_export = latex_export.drop(columns="AMOUNT_normalized")
latex_export[["115_signatures_received"]] = latex_export[["115_signatures_received"]].astype(int)
latex_export[["115_signatures_given"]] = latex_export[["115_signatures_given"]].astype(int)
latex_export[["cosponsors_by_party_D"]] = latex_export[["cosponsors_by_party_D"]].astype(int)
latex_export[["cosponsors_by_party_R"]] = latex_export[["cosponsors_by_party_R"]].astype(int)
latex_export = latex_export.rename(columns={"in_congress_last_five_periods": "Reelection","name": "Name", "party": "Party", "number_of_bills": "Bills", "115_signatures_received": "Received", "115_signatures_given": "Given", "AMOUNT": "Money","cosponsors_by_party_D": "CS D","cosponsors_by_party_R": "CS R", "importance": "Imp_{Rep}", "BillImportance": "Imp_{Bill}", "overallImportance": "Imp"})
print(latex_export.to_latex(index=False,caption="Top ten most important members",longtable=True,bold_rows=True))


# In[ ]:




