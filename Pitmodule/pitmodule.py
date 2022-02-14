from operator import is_
import pandas as pd
import os, re
import numpy as np


DICTTYPE= type({})
LISTTYPE = type([])
TUPLETYPE = type(())
DFTYPE = type(pd.DataFrame())
uni_paths = {"Gminy":[],"Powiaty":[],"Miasta":[],"Wojewodztwa":[],"Metropolia":[]}
filePaths = os.listdir("./data")
POPULATION = "ludnosc_stan_struktura"

def check_data_pit(data_pit):
    return type(data_pit) == DFTYPE and not data_pit.empty 


def check_main_frame(main_frame):
    cond = False
    if type(main_frame) == DICTTYPE and main_frame != {}:
        for df in main_frame.values():
            if check_data_pit(df):
                cond= True
    return cond

class PitFrame:
    def __init__(self,is_path=True,main_path=".",year=2020):
        self.data = {}
        self.uni_paths = {"Gminy":[],"Powiaty":[],"Miasta":[],"Wojewodztwa":[],"Metropolia":[]}
        self.data_path= "."
        self.is_built = False
        self.is_simplified = False
        self.key_columns = []
        self.year = year
        
        if(is_path):
            self.build_paths(main_path,year)    
            self.build_data()
            assert(self.is_built)
            self.simplify_frame()
            self.divide_cities()
            
        
    def build_paths(self,main_path,year):
        self.data_path = main_path + "/data"
        assert(os.path.exists(self.data_path))
        self.file_paths = os.listdir(self.data_path)
        self.assign_paths(year)
        assert(self.are_paths_assigned())
        self.year = year
            
    def assign_paths(self,year):
        for expr in uni_paths:
            self.uni_paths[expr]= [x for x in self.file_paths if (expr in x and "_"+str(year) in x)][0]
    
    def are_paths_assigned(self):
        cond = True
        for x in self.uni_paths.values():
            if x == []:
                cond=False
        return cond
    
    def build_data(self):
        if (not self.is_built):
            for x in self.uni_paths: 
                workbookPath =  self.data_path + "/" + self.uni_paths[x]
                self.data[x] = pd.read_excel(workbookPath)
            
            self.is_built =  True if check_main_frame(self.data) else False
    
    def simplify_header(self,df):
        map_col_names = {df.columns[0]:'wk',df.columns[1]:'pk',df.columns[2]:'gk',df.columns[3]:'gt',
                   df.columns[4]:'jst',df.columns[5]:'wojewodztwo',df.columns[6]:'powiat',
                   df.columns[7]:'klDzial',df.columns[8]:'klRozdzial',df.columns[9]:'klParagraf',
                   df.columns[10]:'naleznosci',df.columns[11]:'dochodyWyk',df.columns[12]:'saldoNaleznosciOgolem',
                   df.columns[13]:'saldoZaleglosciNetto',df.columns[14]:'saldoNadplaty'
                   }
        df.rename(columns=map_col_names,inplace=True)
        df.drop(df.index[0:6],inplace=True)
        df.reset_index(drop=True,inplace=True)
        self.key_columns += list(set(df.columns) -set(['wk','pk','gt','klDzial','klParagraf','saldoZaleglosciNetto']))
        return df
    
    def simplify_frame(self):
        if(not self.is_simplified):
            for x in self.data.values():
                x = self.simplify_header(x)
                assert check_data_pit(x)
            self.is_simplified = True
    
    def shapes(self):
        return [x[0].shape for x in self.data.values()] 
    
    def divide_cities(self):
        if "Miasta" in self.data:
            miastaDF = self.data["Miasta"]
            self.data['Miasta_Gminy'] = miastaDF.loc[miastaDF["klRozdzial"]==75621]
            self.data['Miasta_Powiaty'] = miastaDF.loc[miastaDF["klRozdzial"]==75622]
            del self.data['Miasta']
                  
    def get_PIT(self):
        p = PitFrame(is_path=False,year=self.year)
        for key_df in self.data.keys():
            p.data[key_df] = self.data[key_df][["jst","wojewodztwo","powiat","naleznosci"]]
        return p
    
    def compare(self, _o):
        p = self.get_PIT() 
        o  = _o.get_PIT()
        tmp = PitFrame(is_path=False)
        assert self == _o
        
        for x in self.data.keys():
            key_cols = ['jst','powiat','wojewodztwo']
            suf = (str(self.year),str(o.year))
            tmp.data[x] = p.data[x].merge(o.data[x],on=key_cols,suffixes=suf)
        del p,o
        
        # crating new column
        for x in tmp.data.keys():
            tmp.data[x]["Roznica(%)"] = tmp.data[x]['naleznosci2020']/tmp.data[x]['naleznosci2019'] - 1
        
        return tmp  
    
    def __eq__(self,_o):
        cond = self.data.keys() == _o.data.keys()
        if(cond):
            for x in self.data.keys():
                if not cond:
                    break 
                cond = self.data[x].shape == _o.data[x].shape
        return cond
    
    def save_xlsx():
        pass
