import pandas as pd 
from .pitframe import PitFrame
import numpy as np
import typing

PROG_POD = 0.17
UDZIAL = {
    'Gminy':0.3925,
    'Powiaty':0.1025,
    'Wojewodztwa':0.016
}

def clear_symbols(x):
    data = x.split(".")
    if len(data) > 0:
        return data[1].lower()
    return x

def make_code_book(names):
        codes = [str(2*x).zfill(2) for x in range(1,17)]
        return dict(zip(names,codes))

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
                '85iwięcej',
                '90iwięcej',
                '95iwięcej',
                '85-89',
                '90-94',
                '95-99',
                '100latiwięcej'
            ]

class PopulationFrame:
    def __init__(self, path = "./data/ludnosc_stan_struktura/",is_path=True,tabs= default_tables):
        self.data = {}
        self.is_built = False
        self.tabs = tabs
        self.avg_inc = {}
        self.var = {}
        if is_path:
            self.path = path
            self._read_data2()
            self._short_id()
            #self._merge_duze_miasta()
            self._short_gminy()

    def shapes(self):
        return [x.shape for x in self.data.values()] 

    # edit all 
    def _read_data2(self):
        tabs = self.tabs
        for jst in ['Gminy','Powiaty']:
            jst_frame = pd.DataFrame()
            
            with pd.ExcelFile("./data/ludnosc_stan_struktura/"+tabs[jst]) as xls:
                for sheet in xls.sheet_names:
                    tmp = pd.read_excel(xls,sheet_name=sheet,skiprows=7,usecols="A:C",converters={'Unnamed: 0':str,'Unnamed: 1':str,'Unnamed: 2':str})
                    m={tmp.columns[0]:"jst",
                            tmp.columns[1]: "id",
                            tmp.columns[2]: "ludnosc"}

                    tmp = tmp.rename(columns= m)
                    tmp['id'] = tmp['id'].astype('str')
                    tmp.iloc[:,1] = tmp.iloc[:,1].str.replace(' ','')
                    tmp.iloc[:,1] = tmp.iloc[:,1].str.replace('nan','')
                    tmp.iloc[:,0] = tmp.iloc[:,0].str.replace(' ','')
                    tmp.iloc[:,0] = tmp.iloc[:,0].str.replace('Powiat','')

                    tmp = tmp[ tmp.iloc[:,1].apply(lambda x: len(str(x)) > 0 and not pd.isnull(x)) | tmp.iloc[:,0].isin(age_cond)]
                    tmp.loc[tmp['id'].apply(lambda x: len(x) == 7),'ludnosc'] = 0
                    tmp.reset_index(drop=True,inplace=True)

                    tmp.reset_index(drop=True,inplace=True)
                    val = tmp.iloc[0,1]
                    name =tmp. iloc[0,0]
                    df_dict = tmp.to_dict(orient='records')
                    for row in df_dict:
                        if row['id'] == '' or pd.isnull(row['id']):
                            row['id'] = val
                            row['jst'] = name
                        else:
                            val = row['id']
                            row['ludnosc'] = 0
                            name = row['jst']
                    tmp = pd.DataFrame(df_dict)
                    tmp['ludnosc'] = tmp['ludnosc'].astype(int)
                    tmp  = tmp.groupby(["id","jst"],as_index=False)["ludnosc"].sum()
                    tmp = tmp[tmp['ludnosc'] > 0 ]
                    jst_frame = jst_frame.append(tmp)
                    jst_frame.reset_index(drop =True ,inplace = True)
                        
            self.data[jst]= jst_frame

        jst_frame = pd.DataFrame()
        # seperately treat Wojewodztwa
        with pd.ExcelFile("./data/ludnosc_stan_struktura/tabela03.xls") as xls:
            for sheet in xls.sheet_names:
                tmp = pd.read_excel(xls,sheet_name=sheet,skiprows=7,usecols="A:B",converters={'Unnamed: 0':str,'Unnamed: 1':int})
                m={tmp.columns[0]:"jst",
                        tmp.columns[1]: "ludnosc"}

                tmp = tmp.rename(columns= m)
                tmp.iloc[:,0] = tmp.iloc[:,0].str.replace(' ','')
                tmp.iloc[:,0] = tmp.iloc[:,0].str.replace('\t','')
                tmp.iloc[:,0] = tmp.iloc[:,0].str.replace('\n','')

                tmp = tmp[tmp.iloc[:,0].isin(age_cond + xls.sheet_names)]
                
                df_dict = tmp.to_dict(orient='records')
                name = ''
                for row in df_dict:
                    if row['jst'] in xls.sheet_names:
                        name = row['jst']
                        row['ludnosc'] = 0
                    else:
                        row['jst'] = name
                tmp = pd.DataFrame(df_dict)
                tmp  = tmp.groupby(["jst"],as_index=False)["ludnosc"].sum()
                jst_frame = jst_frame.append(tmp)
                jst_frame.reset_index(drop=True,inplace=True)

                code_book = make_code_book(xls.sheet_names)
                jst_frame['id'] = jst_frame['jst']
                jst_frame['id'] = jst_frame['id'].map(code_book)

        self.data['Wojewodztwa'] = jst_frame

    def _unite_cities(self):
        pass
    
    def _short_id(self):
        self.data['Gminy']['short id'] = self.data['Gminy']['id'].str[:4]
        self.data['Powiaty']['short id'] = self.data['Powiaty']['id'].str[:2]

    def _merge_duze_miasta(self):
        # wycigamy miasta_npp z gmin 
        # dla Powiatow nie musimy tego robic bo 
        if 'short id' not in self.data["Gminy"]:
            self._short_id()
        lud_gminy = self.data["Gminy"]

        # warszawa
        lud_warszawy = lud_gminy[lud_gminy['id'].str[6].isin(['8'])]
        lud_gminy = lud_gminy[~lud_gminy['id'].str[6].isin(['8'])]
        lud_warszawy = lud_warszawy.groupby(['short id'],as_index=False)['ludnosc'].sum()
        lud_warszawy['jst'] = 'Warszawa'
        lud_gminy = lud_gminy.append(lud_warszawy)

        #reszta miast
        lud_miasta = lud_gminy[lud_gminy['id'].str[6].isin(['9'])]
        lud_gminy = lud_gminy[~lud_gminy['id'].str[6].isin(['9'])]
        lud_miasta['jst'] = lud_miasta['jst'].map(lambda x: x.split('-')[0])
        lud_miasta = lud_miasta.groupby(['short id','jst'],as_index=False)['ludnosc'].sum()
        lud_gminy = lud_gminy.append(lud_miasta)
        
        self.data['Gminy']= lud_gminy  

    def _short_gminy(self):
        lud_gminy = self.data['Gminy']
        self.data['Gminy'] = lud_gminy[~lud_gminy['id'].str[6].isin(['8','9'])]
        
    def pull_miasta_npp(self,miasta_npp :pd.DataFrame):
        #miasta_npp zbior miast-gmin ktore funkcjonuje na prawach powiatu na podstawie nich 
        pass
    
    def count_avg_gminy(self,pitGminy,pitMiastaGminy):
        if 'Gminy' not in self.avg_inc:
            plp_gminy = self.data['Gminy'] 
            gminy_not_cities = plp_gminy.merge(pitGminy,on='id')
            gminy_cities = plp_gminy.merge(pitMiastaGminy,left_on='short id',right_on = 'id')
            
            gminy_all_data = gminy_not_cities.append(gminy_cities)
            
            gminy_all_data = gminy_all_data[['jst_x', 'ludnosc','naleznosci','id','short id']]
            gminy_all_data['dochod'] = gminy_all_data['naleznosci']/(PROG_POD*UDZIAL['Gminy'])
            gminy_all_data['dochod_per_capita'] = gminy_all_data['dochod']/gminy_all_data['ludnosc']
            
            self.avg_inc['Gminy'] = gminy_all_data
        return self.avg_inc['Gminy']

    def count_avg_powiaty(self,pitPowiaty ,pitMiastaPowiaty):
        if 'Powiaty' not in self.avg_inc:
            plp_powiaty = self.data['Powiaty'] 
            powiaty_not_cities = plp_powiaty.merge(pitPowiaty,on='id')
            powiaty_cities = plp_powiaty.merge(pitMiastaPowiaty,on='id')
            
            powiaty_all_data = powiaty_not_cities.append(powiaty_cities)
            
            powiaty_all_data = powiaty_all_data[['jst_x', 'ludnosc','naleznosci','id','short id']]
            powiaty_all_data['dochod'] = powiaty_all_data['naleznosci']/(PROG_POD*UDZIAL['Powiaty'])
            powiaty_all_data['dochod_per_capita'] = powiaty_all_data['dochod']/powiaty_all_data['ludnosc']
            
            self.avg_inc['Powiaty'] =  powiaty_all_data
        return self.avg_inc['Powiaty']
    
    def count_avg_wojewodztwa(self,pitWojewodztwa:pd.DataFrame):
        if 'Wojewodztwa' not in self.avg_inc:
            plp_wojew = self.data['Wojewodztwa'] 
            wojew_all_data = plp_wojew.merge(pitWojewodztwa,on='id')
            wojew_all_data = wojew_all_data[['jst_x', 'ludnosc','naleznosci','id']]
            wojew_all_data['dochod'] = wojew_all_data['naleznosci']/(PROG_POD*UDZIAL['Wojewodztwa'])
            wojew_all_data['dochod_per_capita'] = wojew_all_data['dochod']/wojew_all_data['ludnosc']
            self.avg_inc['Wojewodztwa'] =  wojew_all_data
        return self.avg_inc['Wojewodztwa']


    def variance_wojewodztwa(self):
        if 'Wojewodztwa' not in self.var:
            avg_wojewodztwa = self.avg_inc['Wojewodztwa']
            avg_gminy = self.avg_inc['Powiaty']
            avg_wojewodztwa = avg_wojewodztwa[['jst_x','id','dochod_per_capita']]
            avg_gminy = avg_gminy[['jst_x','short id','dochod_per_capita']]
            var_wojewodztwa = pd.merge(avg_wojewodztwa,avg_gminy,left_on='id', right_on='short id',suffixes=('_pow','_gm'))
            var_wojewodztwa['part_var'] = (var_wojewodztwa['dochod_per_capita_gm'] - var_wojewodztwa['dochod_per_capita_pow']).pow(2)
            var_wojewodztwa = var_wojewodztwa.groupby(['short id','jst_x_pow'],as_index=False)['part_var'].mean()
            self.var['Wojewodztwa'] = var_wojewodztwa
        return self.var['Wojewodztwa']

    def var_powiaty(self):
        if 'Powiaty' not in self.var:
            avg_powiaty = self.avg_inc['Powiaty']
            avg_gminy = self.avg_inc['Gminy']
            avg_powiaty = avg_powiaty[['jst_x','id','dochod_per_capita']]
            avg_gminy = avg_gminy[['jst_x','short id','dochod_per_capita']]
            var_Powiaty = pd.merge(avg_powiaty,avg_gminy,left_on='id', right_on='short id',suffixes=('_pow','_gm'))
            var_Powiaty['part_var'] = (var_Powiaty['dochod_per_capita_gm'] - var_Powiaty['dochod_per_capita_pow']).pow(2)
            var_Powiaty = var_Powiaty.groupby(['short id','jst_x_pow'],as_index=False)['part_var'].mean()
            self.var["Powiaty"] = var_Powiaty 
        return self.var["Powiaty"]
            
        
 
        
    
