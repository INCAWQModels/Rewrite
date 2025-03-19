import os

from model import *
from multiprocessing import Pool

def testBed():

    fileName = 'INCAFormatParSet.json'

    if (os.path.isfile(fileName) == True):
        M=Model('INCAFormatParSet.json')

        subcatchments=M.catchment.subcatchments.__len__()
        landCoverTypes=M.catchment.subcatchments[0].landCoverTypes.__len__()
        buckets=M.catchment.subcatchments[0].landCoverTypes[0].buckets.__len__()

        print("Number of subcatchments    :",subcatchments )
        print("Number of land cover types :",landCoverTypes)
        print("Number of buckets          :",buckets)

        for i in range(landCoverTypes):
            print(M.catchment.subcatchments[0].landCoverTypes[i].name)
            for j in range(buckets):
                print("\t", M.catchment.subcatchments[0].landCoverTypes[i].buckets[j].name,
                  "\t", M.catchment.subcatchments[0].landCoverTypes[i].buckets[j].soilTemperatureEffectiveDepth)

        print("About to run...")
        M.run()
        print("... ran")
    
        with ProcessPoolExecutor() as executor:
            #executor.map(self.catchment.solveCatchments,subcatchmentIDs)
            pass
    else:
        print(fileName, " not found")

if __name__ == '__main__':
    testBed()