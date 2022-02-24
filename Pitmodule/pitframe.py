from distutils.command.build import build
from tabnanny import check
from matplotlib.pyplot import subplots_adjust
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
        self._jst_paths = {"Gminy":[],"Powiaty":[],"Miasta":[],"Wojewodztwa":[],"Metropolia":[]}
        self._data_path=main_path
        self._is_built = False
        self._is_simplified = False
        self._key_columns = ['gt','jst','wojewodztwo',"powiat","naleznosci"]
        self.year = 0
        
        if(is_path):
            self.year = year
            self._build_paths(main_path,year)    
            self._build_data()
            assert(self._is_built)
            
            self._simplify_frame()
            self._divide_cities()
            self._check_types()

            self._make_id()
            self._short_frame()
            self._lower()

    def is_built(self):
        return self._is_built
        
    def _build_paths(self,main_path,year):
        self._data_path = main_path + "/data"
        assert(os.path.exists(self._data_path))
        self.file_paths = os.listdir(self._data_path)
        self._assign_paths(year)
        assert(self.are_paths_assigned())
        self.year = year
            
    def _assign_paths(self,year):
        for expr in self._jst_paths:
            self._jst_paths[expr]= [x for x in self.file_paths if (expr in x and "_"+str(year) in x)][0]
    
    def are_paths_assigned(self):
        cond = True
        for x in self._jst_paths.values():
            if x == []:
                cond=False
        return cond
    
    def _build_data(self):
        if (not self._is_built):
            for x in self._jst_paths: 
                workbookPath =  self._data_path + "/" + self._jst_paths[x]
                self.data[x] = pd.read_excel(workbookPath)
            
            self._is_built =  True if check_main_frame(self.data) else False
    
    def _simplify_frame(self):
        if(not self._is_simplified):
            for x in self.data.keys():
                self._simplify_header(x)
                assert check_data_pit(self.data[x])
            self._is_simplified = True
    
    
    def _simplify_header(self,key_df):
        df = self.data[key_df]
        map_col_names = {df.columns[0]:'wk',df.columns[1]:'pk',df.columns[2]:'gk',df.columns[3]:'gt',
                   df.columns[4]:'jst',df.columns[5]:'wojewodztwo',df.columns[6]:'powiat',
                   df.columns[7]:'klDzial',df.columns[8]:'klRozdzial',df.columns[9]:'klParagraf',
                   df.columns[10]:'naleznosci',df.columns[11]:'dochodyWyk',df.columns[12]:'saldoNaleznosciOgolem',
                   df.columns[13]:'saldoZaleglosciNetto',df.columns[14]:'saldoNadplaty'
                   }
        df.rename(columns=map_col_names,inplace=True)
        
        df.reset_index(drop=True, inplace = True)
        df.drop(df.index[0:6],inplace=True)
        
        df.reset_index(drop=True,inplace= True)
        self.data[key_df] = df

    
    def _make_id(self):
        if 'id' not in self._key_columns and 'id' not in self.data['Gminy'].columns:
            for x in self.data.keys():
                self.data[x] = self.data[x].astype({'wk':str,'pk':str,'gk':str,'gt':str})
                self.data[x]['id'] = self.data[x]['wk'] + self.data[x]['pk'] + self.data[x]['gk']+self.data[x]['gt']
                self.data[x]['id'] = self.data[x]['id'].apply(lambda x: x.rstrip('-'))

            self._key_columns += ['id']
            
        

    def _short_frame(self):
        for x in self.data.keys():
            self.data[x] = self.data[x][self._key_columns]


    def _lower(self):
        for x in self.data.values():
            x['jst'] = x['jst'].str.lower()
    
    def shapes(self):
        return [x.shape for x in self.data.values()] 
    
    def _divide_cities(self):
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
    
    def compare(self, other):
        assert self == other and self.year != other.year
        res = {}
        s_suff = str(self.year)
        o_suff = str(other.year)
        for x in self.data.keys():
            sub_data = self.data[x][['id','naleznosci']]
            res[x] = pd.merge(sub_data,right=other.data[x],
                                    on='id',
                                    suffixes=(s_suff,o_suff))

            res[x]["Roznica(%)"] = res[x]['naleznosci'+s_suff]/res[x]['naleznosci'+o_suff] - 1
        
        return res 
    
    def __eq__(self,other):
        cond = self.data.keys() == other .data.keys()
        if(cond):
            for x in self.data.keys():
                if not cond:
                    break 
                cond = self.data[x].shape == other .data[x].shape
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
    
    def _check_types(self):
        for x in self.data.keys():
            self.data[x] = self.data[x].astype({'naleznosci':float,'jst':str,'wk':str,'pk':str,'gk':str,'gt':str})
    
    def count_tax_income(self):
        tt= 0.17 # stands for tax treshold
        
        for x in self.data.keys():
            self.data[x]['dochod'] = self.data[x]['naleznosci'].apply(lambda x: x/tt)
    
            
            




