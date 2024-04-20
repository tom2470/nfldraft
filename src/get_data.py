import pandas as pd
from bs4 import BeautifulSoup, Comment
import requests
import numpy as np
import time
def my_func(url):
  response = requests.get(url)
  time.sleep(20)
  soup = BeautifulSoup(response.text, 'html.parser')
  comments = soup.find_all(string=lambda element: isinstance(element, Comment))
  df=pd.DataFrame()
  list_of_dfs = []
  try:
    list_of_dfs.append(pd.read_html(url)[0])
  except:
    return df
  for comment in comments:
      try:
          tables = pd.read_html(comment)
          for table in tables:
              list_of_dfs.append(table)
      except ValueError:
          pass
  for i in range(len(list_of_dfs)):
    my_data=np.array(list_of_dfs[i]).reshape(1, -1)
    columns=[]
    for k in list_of_dfs[i].columns:
      try:
        columns.append('_'.join([str(ele) for ele in k]))
      except TypeError:
        return df
    list_of_dfs[i].columns=columns
    new_columns=[]
    for k in list_of_dfs[i]['Unnamed: 3_level_0_Class']:
      for j in list_of_dfs[i].columns:
        new_columns.append(f'{k}_{j}')
    df=df.append(pd.DataFrame(data=my_data, columns=new_columns), ignore_index=True)
    result = pd.concat([df[col].astype(str) for col in df.columns], axis=1).stack().dropna().to_frame().T
    result = result.filter(regex='^(?!.*Unnamed).*$')
    result =result.filter(regex='^(?!.*nan).*$')
    result=result.fillna(0)
    return result
def main():
  years= np.arrange(2013, 2023, 1)
  for i in years:
    url2=f'https://www.pro-football-reference.com/years/{i}/draft.htm'
    response2 = requests.get(url2)
    soup = BeautifulSoup(response2.content, features="lxml")
    headers = [th.getText() for th in soup.findAll('tr', limit=2)[1].findAll('th')]
    draft_rows = soup.findAll('tr')[2:]
    draft_rows_csv = [[td.getText() for td in draft_rows[i].findAll(['td', 'th'])]for i in range(len(draft_rows))]
    bad=['\n','Rnd','\n','Pick','\n','Tm','\n','Player','\n','Pos','\n','Age','\n','To','\n','AP1','\n','PB','\n','St','\n','wAV','\n','DrAV','\n','G','\n','Cmp','\n','Att','\n','Yds','\n','TD','\n','Int','\n','Att','\n','Yds','\n','TD','\n','Rec','\n','Yds','\n','TD','\n','Solo','\n','Int','\n','Sk','\n','College/Univ','\n','\n']
    cleaned_draft_rows=[]
    href_value=[]
    for row in draft_rows_csv:
      if row !=bad:
        cleaned_draft_rows.append(row)
    for i in range(len(draft_rows)):
        link_element = draft_rows[i].findAll('a')
        try:
          href_value.append(link_element[3].get('href'))
        except:
          href_value.append('none')
    import warnings
    warnings.filterwarnings("ignore", category=FutureWarning)
    df=pd.DataFrame(cleaned_draft_rows)
    df['href']=href_value
    dfs = []
    for i in range(len(df)):
        print(i)
        row = df.iloc[i]
        try:
          processed_row = my_func(row['href'])
        except:
          processed_row=pd.DataFrame()
        concatenated_row = pd.concat([row.to_frame().T, processed_row], axis=1)
        if concatenated_row.shape[0] == 2:
            concatenated_row = concatenated_row.T.bfill().T.bfill()
            concatenated_row = concatenated_row.drop(concatenated_row.index[1])
        concatenated_row.reset_index(drop=True, inplace=True)
        dfs.append(concatenated_row)

    dfs_length = len(dfs)
    my_df=pd.DataFrame()
    for i, df in enumerate(dfs, start=1):  # Start index from 1
        df.reset_index(drop=True, inplace=True)
        if i == 1 and df.empty:  # Check if df is empty
            df_single_row.index = [dfs_length]
        df = df.loc[:,~df.columns.duplicated()]
        df.index = [i]
        my_df = pd.concat([my_df, df], ignore_index=True)
    my_df.to_csv(f'data/result{i}.csv', index=False)
main()