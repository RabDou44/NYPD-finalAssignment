import pandas as pd 
from .pitframe import PitFrame
import numpy as np

class PopulationFrame:
    def __init__(self, path = "./data",is_path=True):
        self.data = {}
        self.is_built = False
        if is_path:
            self.path = path + "/ludnosc_stan_struktura"
            self.read_data()
            self.__reddit()
    
    def read_data(self):
        self.data["Gminy"] = pd.read_excel(self.path + "/Tabela_IV.xls",skiprows=7)
        self.data["Powiaty"] = pd.read_excel(self.path + "/Tabela_III.xls",skiprows=7)
        self.data["Wojewodztwa"] = pd.read_excel(self.path + "/Tabela_II.xls",skiprows=7) 
    
    def shapes(self):
        return [x.shape for x in self.data.values()] 

    # edit all 
    def __reddit(self):
        # axis 1 - col , 0 rows
        powiaty_gminy = {"Gminy":self.data["Gminy"],"Powiaty":self.data["Powiaty"]}
        for name,frame in powiaty_gminy.items():
            lastcol = frame.shape[1]
            frame.rename(columns={frame.columns[0] : "nazwa",
                        frame.columns[1] :"id",
                        frame.columns[2] : "ludnosc"}
                        ,inplace=True)

            frame = frame.loc[frame["id"].notna()]
            frame = frame.drop(frame.iloc[:,3:lastcol],axis=1)
            frame.reset_index(drop=True,inplace=True)
            frame = frame.drop(["id"],axis =1)
            self.data[name]=frame
        
        wojew = self.data["Wojewodztwa"]
        wojew.rename(columns={wojew.columns[0]:"Wojewodztwo",
                              wojew.columns[1]:"ludnosc"},inplace=True)
        
        wojew = wojew.loc[wojew["ludnosc"].notna()]
        wojew = wojew.drop(wojew.iloc[:,2:wojew.shape[1]],axis=1)
        wojew.reset_index(drop=True,inplace=True)
        wojew = wojew.drop(wojew.index[17:],axis=0)
        wojew.reset_index(drop=True,inplace=True)
        self.data["Wojewodztwa"] = wojew
        
    def __differ_gminy(self):
        pass

    def __miasta_powiaty(self):
        m_powiaty = None
        if "Miasta_Powiaty" not in self.data:
            powiaty = self.data["Powiaty"]
            find_miasta = powiaty["nazwa"].str.contains("M\.")
            m_powiaty = powiaty.loc[find_miasta]
            self.data["Powiaty"] = powiaty.data[~find_miasta]    
        else:
            m_powiaty = self.data["Miasta_Powiaty"]
        
        return m_powiaty

    def __gminyformat(self):
        # it' inaccurate cause there is no Metropolia
        if 'gt' not in self.data:
            gmnina_values = [1,2,3]

            gminy = self.data["Gminy"]
            condition = [
                (gminy['nazwa'].str.contains("M\.")),
                (gminy['nazwa'].str.contains("G\.")),
                (gminy['nazwa'].str.contains("M-W\.")),
            ]
            gminy['jst'] = np.select(condition,gmnina_values)

            # clean jst names
            gminy['nazwa'] = gminy['nazwa'].apply(lambda x: x[2:] if 'M\.' in x else x)
            gminy['nazwa'] = gminy['nazwa'].apply(lambda x: x[4:] if 'M-W\.' in x else x)
            gminy['nazwa'] = gminy['nazwa'].apply(lambda x: x[2:] if 'G\.' in x else x)
            self.data['Gminy'] = gminy
            



    def __gminyshort(self):
            m_powiaty = self.data["Miasta_Powiaty"] = self.__miasta_powiaty()
            self.data["Miasta_Gminy"] = m_powiaty['nazwa'] #except those who municipalities with law of a county
            pass

        
        
        
    
