import openpyxl
import pandas as pd
import os
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
        self.__uni_paths = {"Gminy":[],"Powiaty":[],"Miasta":[],"Wojewodztwa":[],"Metropolia":[]}
        self.__data_path=main_path
        self.__is_built = False
        self.__is_simplified = False
        self.__key_columns = ('gt','jst','wojewodztwo',"powiat","naleznosci")
        self.year = 0
        
        if(is_path):
            self.year = year
            self.build_paths(main_path,year)    
            self.__build_data()
            assert(self.__is_built)
            self.__simplify_frame()
            self.__divide_cities()
            self.__short_frame()
            self.__lower()

            
        
    def build_paths(self,main_path,year):
        self.__data_path = main_path + "/data"
        assert(os.path.exists(self.__data_path))
        self.file_paths = os.listdir(self.__data_path)
        self.__assign_paths(year)
        assert(self.are_paths_assigned())
        self.year = year
            
    def __assign_paths(self,year):
        for expr in self.__uni_paths:
            self.__uni_paths[expr]= [x for x in self.file_paths if (expr in x and "_"+str(year) in x)][0]
    
    def are_paths_assigned(self):
        cond = True
        for x in self.__uni_paths.values():
            if x == []:
                cond=False
        return cond
    
    def __build_data(self):
        if (not self.__is_built):
            for x in self.__uni_paths: 
                workbookPath =  self.__data_path + "/" + self.__uni_paths[x]
                self.data[x] = pd.read_excel(workbookPath)
            
            self.__is_built =  True if check_main_frame(self.data) else False
    
    def __simplify_header(self,df):
        map_col_names = {df.columns[0]:'wk',df.columns[1]:'pk',df.columns[2]:'gk',df.columns[3]:'gt',
                   df.columns[4]:'jst',df.columns[5]:'wojewodztwo',df.columns[6]:'powiat',
                   df.columns[7]:'klDzial',df.columns[8]:'klRozdzial',df.columns[9]:'klParagraf',
                   df.columns[10]:'naleznosci',df.columns[11]:'dochodyWyk',df.columns[12]:'saldoNaleznosciOgolem',
                   df.columns[13]:'saldoZaleglosciNetto',df.columns[14]:'saldoNadplaty'
                   }
        df.rename(columns=map_col_names,inplace=True)
        df.reset_index(drop=True, inplace = True)
        df.drop(df.index[0:6],inplace=True)
        # self.key_columns += list(set(df.columns) -set(['wk','pk','gt','klDzial','klParagraf','saldoZaleglosciNetto']))
        return df
    
    def __simplify_frame(self):
        if(not self.__is_simplified):
            for x in self.data.values():
                x = self.__simplify_header(x)
                assert check_data_pit(x)
            self.__is_simplified = True
    
    def __short_frame(self):    
        self.data['Gminy'] = self.data['Gminy'][['gt',"jst","wojewodztwo","powiat","naleznosci"]]
        self.data['Powiaty'] = self.data['Powiaty'][["jst","wojewodztwo","powiat","naleznosci"]]
        self.data['Wojewodztwa'] = self.data['Wojewodztwa'][["jst","wojewodztwo","powiat","naleznosci"]]

    def __lower(self):
        for x in self.data.values():
            x['jst'] = x['jst'].str.lower()
    
    def shapes(self):
        return [x.shape for x in self.data.values()] 
    
    def __divide_cities(self):
        if "Miasta" in self.data:
            miastaDF = self.data["Miasta"]
            self.data['Miasta_Gminy'] = miastaDF.loc[miastaDF["klRozdzial"]==75621]
            self.data['Miasta_Gminy'].reset_index(drop=True,inplace= True)
            self.data['Miasta_Powiaty'] = miastaDF.loc[miastaDF["klRozdzial"]==75622]
            self.data['Miasta_Powiaty'].reset_index(drop=True,inplace= True)
            del self.data['Miasta']
                  
    def get_PIT(self):
        p = PitFrame(is_path=False,year=self.year)
        for key_df in self.data.keys():
            if key_df == "Gminy":
                p.data[key_df] = self.data[key_df][['gt',"jst","wojewodztwo","powiat","naleznosci"]]
            else:
                p.data[key_df] = self.data[key_df][["jst","wojewodztwo","powiat","naleznosci"]]
        return p
    
    def compare(self, _o):
        p = self.get_PIT() 
        o  = _o.get_PIT()
        tmp = PitFrame(is_path=False)
        tmp.year = (str(self.year),str(_o.year))
        assert self == _o
        
        for x in self.data.keys():
            key_cols = ['jst','powiat','wojewodztwo']
            if x == 'Gminy':
                key_cols += 'gt'
            suf = (str(self.year),str(o.year))
            tmp.data[x] = pd.merge(left=p.data[x],right=o.data[x],
                                    on=key_cols,
                                    suffixes=tmp.year)
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
    
    def save_xlsx(self,path = "./",name = "pitframe"):
        path_name = path + name + str(self.year) + ".xlsx"
        dirs = os.path.dirname(path_name)
        if not os.path.exists(path_name):
            os.makedirs(dirs,exist_ok=True)
        
        openpyxl.Workbook().save(path_name)

        with pd.ExcelWriter(path_name,engine = 'openpyxl') as writer:
            for key in self.data:
                self.data[key].to_excel(writer,sheet_name = str(key))

