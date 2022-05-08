import pandas as pd
import re
from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components
import holoviews as hv
hv.extension('bokeh', logo=False)
import hvplot.pandas

st.markdown("## Full Network of Top 20 Shareholders of the ASX200")

# Helper functions
##############################################################
def extender_color_list(color_list, length_required):
    extended_color_list = []
    while True:
        for color in color_list:
            if len(extended_color_list) == length_required:
                return extended_color_list
            else:
                extended_color_list.append(color)
       
    

def string_cleaner(string, words_to_remove = []):
    string = str(string).lower()
    
    string = re.sub("<.+>|\(.+\)", "", string)
    
    string_list_space = string.split(" ")
    
    string_list = [word for word in string_list_space if word != ""]
    
    string_list_words_remove = [word.capitalize() for word in string_list if word not in words_to_remove]
    
    final_string = " ".join(string_list_words_remove)
    
    return final_string
                
def clean_up_df(df):
    # Drop empty cells
    df_drop = df.dropna()
    
    # Drop rows which have either:
        # No shareholder information 
        # No Top 20 shareholder information 
    # These are present in the Name column
    # But also present with 0 shares
    
    df_drop_0 = df_drop[df_drop["Shares"] != 0]
    return df_drop_0
#################################################################

import pandas as pd
import re

shareholders_df_raw = pd.read_csv("shareholders.csv")
shareholders_df = clean_up_df(shareholders_df_raw)

ticker_asx200 = list(set(shareholders_df["Ticker"]))

shareholders_clean = []
for shareholder in list(shareholders_df["Name"]):
    shareholder_clean = string_cleaner(str(shareholder), ['custody', 'nominees', 'limited', 'pty', 'ltd'])
    shareholders_clean.append(shareholder_clean)
    
shareholders_df["Name_clean"] = shareholders_clean

unique_shareholders_asx200 = list(set(shareholders_df["Name_clean"]))

tickers_and_shareholders = ticker_asx200 + unique_shareholders_asx200

nodes_tickers_and_shareholders = list(range(len(tickers_and_shareholders)))

color_list = ["#FF0000", "#FFFFFF", "#00FFFF"
              , "#C0C0C0","#0000FF","#808080"
              ,"#00008B","#ADD8E6","#FFA500"
              ,"#800080","#A52A2A","#FFFF00"
              ,"#800000","#00FF00","#008000"
              ,"#FF00FF","#808000","#FFC0CB"]

extended_color_list = extender_color_list(color_list, len(tickers_and_shareholders))


# Creating the network
from pyvis.network import Network

net = Network(notebook = True, bgcolor="#222222", font_color="white")
#net = Network(notebook = True)

# Add specifications here
# Adding an additional node for ticker chosen
for node, color, label in zip(nodes_tickers_and_shareholders, extended_color_list, tickers_and_shareholders):
    # If label is a ticker in the ASX200
    if label in ticker_asx200:
        # Accessing names related to a ticker which is present in the form of 3 capital letters
        name_list = list(shareholders_df[shareholders_df["Ticker"] == label]["Name_clean"])
        # Accessing capital percentage related to a ticker 
        capital_list = list(shareholders_df[shareholders_df["Ticker"] == label]["Capital"])
        
        title_node = f'{label} <br>Top 20 Shareholders:<br>'
        num = 0
        for shareholder, capital in zip(name_list, capital_list):
            num += 1
            title_node += f'<br>{num}) {shareholder}: {capital}'
            
        img = f"https://files.marketindex.com.au/xasx/96x96-png/{label.lower()}.png"
        
        # Creating the node
        net.add_node(n_id = node, label = label, title = title_node, image = img, shape = 'image')
        
    else:
        # Accessing names related to a non-asx200 company
        ticker_list = list(shareholders_df[shareholders_df["Name_clean"] == label]["Ticker"])
        # Accessing capital percentage related to a company 
        capital_list = list(shareholders_df[shareholders_df["Name_clean"] == label]["Capital"])
        
        title_node = f'{label} <br>Investments:<br>'
        num = 0
        for shareholder, capital in zip(ticker_list, capital_list):
            num += 1
            title_node += f'<br>{num}) {shareholder}: {capital}'
            
        # Creating the node
        net.add_node(n_id = node, color = color, label = label, title = title_node)
    

# Creating a dictionary to know which company is which node
company_nodes_dict = {}
for company, node in zip(tickers_and_shareholders, nodes_tickers_and_shareholders):
    company_nodes_dict[company] = node 

# Adding network edges for each company
for shareholder in unique_shareholders_asx200:
    shareholder_investments = list(shareholders_df[shareholders_df["Name_clean"] == shareholder]["Ticker"])
    shareholder_investments_shares = list(shareholders_df[shareholders_df["Name_clean"] == shareholder]["Shares"])
    shareholder_investments_capital = list(shareholders_df[shareholders_df["Name_clean"] == shareholder]["Capital"])
    
    shareholder_node = company_nodes_dict[shareholder]
    for company, shares, capital in zip(shareholder_investments, shareholder_investments_shares, shareholder_investments_capital):
        company_node = company_nodes_dict[company]
        
        net.add_edge(shareholder_node, company_node, value = shares)
        
        
net.repulsion(node_distance=1500, spring_length=1000)
path = '/tmp'
net.save_graph(f'{path}/pyvis_full_graph.html')

path = '/tmp'
HtmlFile = open(f'{path}/pyvis_full_graph.html','r',encoding='utf-8')

if st.button("Display full network"):
    components.html(HtmlFile.read(), height=600, width = 2000)

























def shareholders_connection_graph(ticker_chosen):
    
    top20_raw = pd.read_csv("shareholders.csv")
    
    shareholders_df = clean_up_df(top20_raw)
    
    ticker_asx200 = list(set(shareholders_df["Ticker"]))

    shareholders_clean = []
    for shareholder in list(shareholders_df["Name"]):
        shareholder_clean = string_cleaner(str(shareholder), ['custody', 'nominees', 'limited', 'pty', 'ltd'])
        shareholders_clean.append(shareholder_clean)

    shareholders_df["Name_clean"] = shareholders_clean

    unique_shareholders_asx200 = list(set(shareholders_df["Name_clean"]))
    
    color_list = ["#FF0000", "#FFFFFF", "#00FFFF", "#C0C0C0","#0000FF","#808080","#00008B"
                  ,"#ADD8E6","#FFA500","#800080","#A52A2A","#FFFF00","#800000","#00FF00","#008000"
                  ,"#FF00FF","#808000","#FFC0CB"]
    
    

    
    # Specifying the number of nodes present in the selected network
    node_label = []
    for ticker in ticker_chosen:
        if ticker in ticker_asx200:
            # Ticker and their nodes
            list_of_shareholders = list(shareholders_df[shareholders_df["Ticker"] == ticker]["Name_clean"])
            node_label += ([ticker] + list_of_shareholders)
        
        else:
            # Shareholders and their nodes
            list_of_shareholders = list(shareholders_df[shareholders_df["Name_clean"] == ticker]["Ticker"])
            node_label += ([ticker] + list_of_shareholders)
            
    # Finalised node label related to tickers_chosen
    node_label = set(list(node_label))

    color_list = ["#FF0000", "#FFFFFF", "#00FFFF", "#C0C0C0","#0000FF","#808080","#00008B"
                  ,"#ADD8E6","#FFA500","#800080","#A52A2A","#FFFF00","#800000","#00FF00","#008000"
                  ,"#FF00FF","#808000","#FFC0CB"]
    
    # Creating length of color list required
    extended_color_list = extender_color_list(color_list, len(node_label))
    
    # Creating range of numbers for nodes
    node_num = list(range(len(node_label)))
    
    # Dictionary to access company's node number
    company_nodes_dict = {}
    
    # Setting up network
    from pyvis.network import Network

    net = Network(notebook = True, bgcolor="#222222", font_color="white")
    
    # Creating nodes related to tickers chosen
    for node, color, label in zip(node_num, extended_color_list, node_label):
    # If label is a ticker in the ASX200
        company_nodes_dict[label] = node
        if label in ticker_asx200:
            # Accessing names related to a ticker which is present in the form of 3 capital letters
            name_list = list(shareholders_df[shareholders_df["Ticker"] == label]["Name_clean"])
            # Accessing capital percentage related to a ticker 
            capital_list = list(shareholders_df[shareholders_df["Ticker"] == label]["Capital"])

            title_node = f'{label} <br>Top 20 Shareholders:<br>'
            num = 0
            for shareholder, capital in zip(name_list, capital_list):
                num += 1
                title_node += f'<br>{num}) {shareholder}: {capital}'

            img = f"https://files.marketindex.com.au/xasx/96x96-png/{label.lower()}.png"

            # Creating the node
            net.add_node(n_id = node, label = label, title = title_node, image = img, shape = 'image')
        
        else:
            # Accessing names related to a non-asx200 company
            ticker_list = list(shareholders_df[shareholders_df["Name_clean"] == label]["Ticker"])
            # Accessing capital percentage related to a company 
            capital_list = list(shareholders_df[shareholders_df["Name_clean"] == label]["Capital"])

            title_node = f'{label} <br>Investments:<br>'
            num = 0
            for shareholder, capital in zip(ticker_list, capital_list):
                num += 1
                title_node += f'<br>{num}) {shareholder}: {capital}'

            # Creating the node
            net.add_node(n_id = node, color = color, label = label, title = title_node)

    
    # Adding network edges for each company
    for shareholder in ticker_chosen:
        if shareholder in ticker_asx200:
            shareholder_investments = list(shareholders_df[shareholders_df["Ticker"] == shareholder]["Name_clean"])
            shareholder_investments_shares = list(shareholders_df[shareholders_df["Ticker"] == shareholder]["Shares"])
            shareholder_investments_capital = list(shareholders_df[shareholders_df["Ticker"] == shareholder]["Capital"])

        else:
            shareholder_investments = list(shareholders_df[shareholders_df["Name_clean"] == shareholder]["Ticker"])
            shareholder_investments_shares = list(shareholders_df[shareholders_df["Name_clean"] == shareholder]["Shares"])
            shareholder_investments_capital = list(shareholders_df[shareholders_df["Name_clean"] == shareholder]["Capital"])
            
        shareholder_node = company_nodes_dict[shareholder]
        for company, shares, capital in zip(shareholder_investments,shareholder_investments_shares,shareholder_investments_capital):
            company_node = company_nodes_dict[company]
            
            net.add_edge(shareholder_node, company_node, value = shares)

    net.repulsion(node_distance=300, spring_length=200)
    path = '/tmp'
    net.save_graph(f'{path}/pyvis_graph.html')

col1, col2 = st.columns(2)

top20_raw = pd.read_csv("shareholders.csv")
    
shareholders_df = clean_up_df(top20_raw)


# Select ticker
ticker_list = list(set(shareholders_df["Ticker"]))
selected_ticker = st.multiselect('Select ticker(s) to visualize', ticker_list)



# Select shareholder
shareholders_list = []
for shareholder in list(shareholders_df["Name"]):
    shareholder_clean = string_cleaner(str(shareholder), ['custody', 'nominees', 'limited', 'pty', 'ltd'])
    shareholders_list.append(shareholder_clean)
        
selected_shareholder = st.multiselect('Select Shareholder(s) to visualize', list(set(shareholders_list)))

# Combine both
ticker_and_shareholder = selected_ticker + selected_shareholder


shareholders_connection_graph(ticker_and_shareholder)

path = '/tmp'
HtmlFile = open(f'{path}/pyvis_graph.html','r',encoding='utf-8')



components.html(HtmlFile.read(), height=600, width = 2000)
    
    
def display_tables(ticker_chosen):
    top20_raw = pd.read_csv("shareholders.csv")
    
    # Drop rows with no information
    shareholders_df = clean_up_df(top20_raw)
    
    name_clean = []
    for name in list(shareholders_df.Name):
        name_clean.append(string_cleaner(name, ['custody', 'nominees', 'limited', 'pty', 'ltd']))
        
    shareholders_df["Name_clean"] = name_clean
    
    # Set up list of tickers with information for use
    ticker_asx200 = list(set(shareholders_df["Ticker"]))
    
    displayed_list = []
    for ticker in ticker_chosen:
        # If ticker chosen is a ASX200 company
        if ticker in ticker_asx200:
            ticker_df = shareholders_df[shareholders_df["Ticker"] == ticker]
            displayed_list.append(ticker_df)
        # If ticker chosen is a shareholder of an ASX200 company
        else:
            ticker_df = shareholders_df[shareholders_df["Name_clean"] == ticker]
            displayed_list.append(ticker_df)
            
    df = pd.concat(displayed_list, axis = 0)
    df = df[["Name", "Shares", "Capital", "Ticker"]].set_index("Name")
    return df

try:
    st.sidebar.table(display_tables(ticker_and_shareholder))
except:
    st.sidebar.write("Table displayed here")


import re
import hvplot.pandas
def graph_insider(ticker_chosen):
    import re
    import hvplot.pandas
    
    insider_df = pd.read_csv("insider.csv")
    
    insider_df["Date"] = pd.to_datetime(insider_df["Date"])
    
    price_list = list(insider_df.Value)
    
    # Change values from string to float numbers
    int_price_list = []
    for price in price_list:
        if re.findall("\(", price):
            # Removing , from values
            price = re.sub(",", "", price)
            # Removing () and $ from negative numbers
            int_price_list.append(float(price[2:-1]))
        else:
            # Removing , from values
            price = re.sub(",", "", price)
            # Removing $ from positive numbers
            int_price_list.append(float(price[1:]))
            
    insider_df["Bought/Sold"] = int_price_list
    
    # Filter for selected tickers
    hvplot_str_list = []
    for ticker in ticker_chosen:
        hvplot_str_list.append(f'insider_df[insider_df["Ticker"] == "{ticker}"].sort_values(by = ["Date"]).set_index("Date").hvplot.bar(y = "Bought/Sold", hover_cols = ["Director", "Price", "Value", "Type"], rot = 90, shared_axes = False, title = f"{ticker} Insider trades")')
        
    hvplot_str = " + ".join(hvplot_str_list) 
    return eval(hvplot_str)

try:
    graph = graph_insider(selected_ticker)
    hv.save(graph ,'fig.html')
    HtmlFile = open("fig.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, width=1800, height=1200, scrolling=True)
except:
    pass
