import pandas as pd 
from .pitframe import PitFrame
import numpy as np

def clear_symbols(x):
    data = x.split(".")
    if len(data) > 0:
        return data[1].lower()
    return x

default_tables ={
    "Gminy":"tabela12.xls",
    "Powiaty":"tabela06.xls",
    "Wojewodztwa":"tabela03.xls"
}

age_cond = ['27','28','29',
                '30-34',
                '35-39',
                '40-44',
                '45-49',
                '50-54',
                '55-59',
                '60-64',
                '65-69',
                '70-74',
                '75-79',
                '80-84',
                '75iwięcej',
                '80iwięcej',
                '85iwięcej'
            ]

class PopulationFrame:
    def __init__(self, path = "./data/ludnosc_stan_struktura/",is_path=True,tabs= default_tables):
        self.data = {}
        self.is_built = False
        self.tabs = tabs
        if is_path:
            self.path = path
            self._read_data2()
            #self.__reddit()
            #self.__gminyformat()
    
    def _read_data(self):
        tabs =self.tabs
        self.data["Gminy"] = pd.read_excel(self.path + tabs['Gminy'],skiprows=7)
        self.data["Powiaty"] = pd.read_excel(self.path + tabs['Powiaty'],skiprows=7)
        self.data["Wojewodztwa"] = pd.read_excel(self.path + tabs['Wojewodztwa'],skiprows=7)
        self.data['Metropolia'] = pd.DataFrame({'jst':["górnośląsko-zagłębiowska\nmetropolia"],"ludnosci" :[2072200],'id':'24'}) 
    
    def shapes(self):
        return [x.shape for x in self.data.values()] 

    # edit all 
    def _read_data2(self):
        tabs = self.tabs
        for jst in tabs:
            jst_frame = pd.DataFrame()
            
            with pd.ExcelFile(self.path +tabs[jst]) as xls:
                for sheet in xls.sheet_names:
                    tmp =pd.read_excel(xls,sheet_name=sheet,skiprows =7,usecols="A:C")
                    
                    # rename columns
                    m={tmp.columns[0]:"jst",
                    tmp.columns[1]: "id",
                    tmp.columns[2]: "populacja"}
                    tmp = tmp.rename(columns= m)

                    tmp = tmp.astype('str')
                    tmp.iloc[:,1] = tmp.iloc[:,1].str.replace(' ','')
                    tmp.iloc[:,0] = tmp.iloc[:,0].str.replace(' ','')

                    #slicing & editing
                    tmp =  tmp[tmp.iloc[:,1].apply(lambda x: len(str(x)) > 0 and not pd.isnull(x)) | tmp.iloc[:,0].isin(age_cond)]
                    
                    #preapare data for swaping values
                    code_len = {'Gminy':7,'Powiaty':4,'Wojewodztwa':2}
                    tmp.loc[tmp['id'].apply(lambda x: len(x) == code_len[jst]),'populacja'] = 0 

                    val = tmp.iloc[0,1]
                    name =tmp. iloc[0,0]
                    df_dict = tmp.to_dict(orient='records')
                    for row in df_dict:
                        if row['id'] == '' or pd.isnull(row['id']):
                            row['id'] = val
                            row['jst'] = name
                        else:
                            val = row['id']
                            row['populacja'] = 0
                            name = row['jst']
                    tmp = pd.DataFrame(df_dict)

                    tmp['populacja'] = tmp['populacja'].astype(int)
                    tmp  = tmp.groupby(by=['id','jst'])['populacja'].sum()
                    jst_frame = jst_frame.append(tmp)
                    jst_frame.reset_index(drop=True,inplace=True)
                
            self.data[jst]= jst_frame


    
    def _reddit(self):
        # axis 1 - col , 0 rows
        powiaty_gminy = {"Gminy":self.data["Gminy"],"Powiaty":self.data["Powiaty"]}
        for name,frame in powiaty_gminy.items():
            lastcol = frame.shape[1]
            frame.rename(columns={frame.columns[0] : "jst",
                        frame.columns[1] :"id",
                        frame.columns[2] : "ludnosc"}
                        ,inplace=True)

            frame = frame.loc[frame["id"].notna()]
            frame = frame.drop(frame.iloc[:,3:lastcol],axis=1)
            frame.reset_index(drop=True,inplace=True)
            frame = frame.drop(["id"],axis =1)
            self.data[name]=frame

        wojew = self.data["Wojewodztwa"]
        wojew.rename(columns={wojew.columns[0]:"jst",
                              wojew.columns[1]:"ludnosc"},inplace=True)
        
        wojew = wojew.loc[wojew["ludnosc"].notna()]
        wojew = wojew.drop(wojew.iloc[:,2:wojew.shape[1]],axis=1)
        wojew.reset_index(drop=True,inplace=True)
        wojew = wojew.drop(wojew.index[17:],axis=0)
        wojew.reset_index(drop=True,inplace=True)
        self.data["Wojewodztwa"] = wojew

        # for x in self.data.keys():
        #     self.data[x] = self.data[x].astype({'jst':str,'ludnosc':int})

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

    def _gminyformat(self):
        # it' inaccurate cause there is no Metropolia
        if 'gt' not in self.data:
            gmnina_values = [1,2,3]

            gminy = self.data["Gminy"]
            condition = [
                (gminy['jst'].str.contains("M\.")),
                (gminy['jst'].str.contains("G\.")),
                (gminy['jst'].str.contains("M-W\.")),
            ]
            gminy['gt'] = np.select(condition,gmnina_values)

            # clean jst names
            gminy['jst']  = gminy['jst'].apply(clear_symbols)
            self.data['Gminy'] = gminy 
  



    

        
        
        
    
