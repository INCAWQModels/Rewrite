
from model import *

M=Model('scratch.json')
M.externalTimeStep.value=86400

subcatchments=M.catchment.subcatchments.__len__()
landCoverTypes=M.catchment.subcatchments[0].landCoverTypes.__len__()
buckets=M.catchment.subcatchments[0].landCoverTypes[0].buckets.__len__()

print("Number of subcatchments    :",subcatchments )
print("Number of land cover types :",landCoverTypes)
print("Number of buckets          :",buckets)

print("Number of data rows        :",M.drivingData.dataTable.__len__())

for i in range(landCoverTypes):
    print(M.catchment.subcatchments[0].landCoverTypes[i].name)