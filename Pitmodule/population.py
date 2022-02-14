import pandas as pd 

class PopulationFrame:
    def __init__(self, path = "./data",is_path=True):
        self.data = {}
        self.is_built = False
        if is_path:
            self.path = path + "/ludnosc_stan_struktura"
            self.read_data()
        self.__cut_clear()
        #self.__cut_rows()
    
    def read_data(self):
        self.data["Gminy"] = pd.read_excel(self.path + "/Tabela_IV.xls",skiprows=7)
        self.data["Powiaty"] = pd.read_excel(self.path + "/Tabela_III.xls",skiprows=7)
        self.data["Wojewodztwa"] = pd.read_excel(self.path + "/Tabela_II.xls",skiprows=7)
        
    
    def __cut_clear(self):
        powiaty_gminy = {"Gminy":self.data["Gminy"],"Powiaty":self.data["Powiaty"]}
        for name,frame in powiaty_gminy.items():
            lastcol = frame.shape[1]
            mapping = {frame.columns[0] : str(name),
                        frame.columns[1] :"id",
                        frame.columns[2] : "ludnosc"}
        
            frame.rename(columns=mapping,inplace=True)
            frame = frame[frame["id"].notna()]
            frame.drop(frame.iloc[:,3:lastcol],axis=1,inplace=True)
            frame.reset_index(drop=True,inplace=True)
            print(frame.columns)
            frame.drop(["id"],axis =1,inplace=True)
            self.data[name]=frame
        
        wojew = self.data["Wojewodztwa"]
        wojew.rename(columns={wojew.columns[0]:"Wojewodztwo",
                              wojew.columns[1]:"ludnosc"},inplace=True)
        
        wojew = wojew[wojew["ludnosc"].notna()]
        wojew.drop(wojew.iloc[:,2:wojew.shape[1]],axis=1,inplace=True)
        wojew.reset_index(drop=True,inplace=True)
        wojew.drop(wojew.index[17:],axis=0,inplace=True)
        wojew.reset_index(drop=True,inplace=True)
        self.data["Wojewodztwa"] = wojew
    
    def __cut_rows(self):
        powiat = self.data["Powiaty"]
        powiat.drop(powiat.loc[:,'id'],axis=1,inplace=True)
        self.data["Powiaty"] = powiat
        gmina = self.data["Gmina"]
        gmina.drop(gmina.loc[:,'id'],axis=1,inplace=True)
        wojew = self.data["Wojewodztwa"]
        wojew.drop(wojew.iloc[17:,:],axis=0,inplace=True)
        self.data["Wojewodztwo"] = wojew
        
    def __differ_gminy(self):
        self.data[""]

        
        
        
    
