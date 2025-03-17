from fib0 import fib

from model import *
from multiprocessing import Pool

def testBed():
    M=Model('pars.json')

    subcatchments=M.catchment.subcatchments.__len__()
    landCoverTypes=M.catchment.subcatchments[0].landCoverTypes.__len__()
    buckets=M.catchment.subcatchments[0].landCoverTypes[0].buckets.__len__()

    print("Number of subcatchments    :",subcatchments )
    print("Number of land cover types :",landCoverTypes)
    print("Number of buckets          :",buckets)

    print("Number of data rows        :",M.drivingData.dataTable.__len__())

    for i in range(landCoverTypes):
        print(M.catchment.subcatchments[0].landCoverTypes[i].name)
        for j in range(buckets):
            print("\t", M.catchment.subcatchments[0].landCoverTypes[i].buckets[j].name,
                  "\t", M.catchment.subcatchments[0].landCoverTypes[i].buckets[j].soilTemperatureEffectiveDepth)

    with ProcessPoolExecutor() as executor:
            #executor.map(self.catchment.solveCatchments,subcatchmentIDs)
            executor.map(fib, [35] * 20)

if __name__ == '__main__':
    testBed()