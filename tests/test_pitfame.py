from xml.etree.ElementTree import PI
import pytest
import pandas as pd
import os
from Pitmodule.pitframe import PitFrame 
from Pitmodule.pitframe import  check_main_frame

DICTTYPE= type({})
LISTTYPE = type([])
TUPLETYPE = type(())
DFTYPE = type(pd.DataFrame())
uni_paths = {"Gminy":[],"Powiaty":[],"Miasta":[],"Wojewodztwa":[],"Metropolia":[]}
filePaths = os.listdir("./data")
POPULATION = "ludnosc_stan_struktura"

def test_always_passes():
    assert True

def test_always_fails():
    assert False

def test_pitframe_built():
    p = PitFrame(year=2019)
    assert check_main_frame(p.data) == True and p.year == 2019 

def test_get_PIT():
    p = PitFrame() 
    pit = p.get_PIT()
    assert check_main_frame(pit)
    formatCols = ['gt','jst','wojewodztwo',"powiat","naleznosci"]
    assert pit.data["Gminy"].index == formatCols
    formatCols.pop(0)
    for x in p.data:
        if x != 'Gminy':
            p.data[x].index == formatCols
    

def test_save_xlsx():
    pit = PitFrame(2020)
    pit.save_xlsx(name='test')
    pit_path = './' + 'test' + str(2020) +'.xlsx'
    assert os.path.exists(pit_path)