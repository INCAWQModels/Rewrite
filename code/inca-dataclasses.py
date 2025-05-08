from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union


class Model:
    def __init__(self, repository: str = "https://github.com/INCAWQModels/Rewrite",
                 branch: str = "main",
                 commit: str = "6a80d0f",
                 catchment: Optional["Catchment"] = None):
        self.repository = repository
        self.branch = branch
        self.commit = commit
        self.catchment = catchment if catchment is not None else Catchment(name="Default Catchment")


@dataclass
class General:
    name: str = "New parameter set"
    creator: str = "Anonymous"
    timeStep: float = 86400
    internalTimeStepMultiplier: float = 1.0
    startDate: str = "2020-01-01 00:00:00"
    model: Model = field(default_factory=Model)
    chemistry: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BucketIdentifier:
    name: str
    abbreviation: str


@dataclass
class BucketGeneral:
    receivesPrecipitation: bool = False


@dataclass
class Bucket:
    identifier: BucketIdentifier
    general: BucketGeneral


@dataclass
class LandCoverIdentifier:
    name: str
    abbreviation: str


@dataclass
class SoilTemperatureModel:
    C_s: float = 1.0e07
    K_t: float = 0.6
    C_ice: float = 9.0e06
    f_s: float = -3.0


@dataclass
class EvapotranspirationModel:
    temperatureOffset: float = 0.0
    scalingFactor: float = 70.0


@dataclass
class LandCoverGeneral:
    soilTemperatureModel: SoilTemperatureModel
    evapotranspirationModel: EvapotranspirationModel


@dataclass
class Precipitation:
    degreeDayMeltFactor: float = 3.0
    rainfallMultiplier: float = 1.0
    snowfallMultiplier: float = 1.0
    snowfallTemperature: float = 0.0
    snowmeltTemperature: float = 0.0
    snowmeltRate: float = 3.0
    snowDepth: float = 0.0


@dataclass
class Routing:
    flowMatrix: List[List[float]]  # This remains a matrix of flow values


@dataclass
class BucketGeneralConfig:
    initialSoilTemperature: float = 5.0
    relativeAreaIndex: float = 1.0
    soilTemperatureEffectiveDepth: float = 30.0


@dataclass
class Hydrology:
    characteristicTimeConstant: float = 1.0
    tightlyBoundWaterDepth: float = 10.0
    looselyBoundWaterDepth: float = 50.0
    freelyDrainingWaterDepth: float = 50.0
    initialWaterDepth: float = 100.0
    relativeETIndex: float = 0.0
    ETScalingExponent: float = 1.0
    infiltrationThresholdTemperature: float = 0.0


@dataclass
class ChemistryGeneral:
    soilTemperatureOffset: float = 20.0
    soilTemperatureExponent: float = 2.0


@dataclass
class BucketChemistry:
    general: ChemistryGeneral


@dataclass
class LandCoverBucket:
    general: BucketGeneralConfig
    hydrology: Hydrology
    soilOrSediment: Dict[str, Any] = field(default_factory=dict)
    chemistry: BucketChemistry = field(default_factory=BucketChemistry)


@dataclass
class LandCover:
    identifier: LandCoverIdentifier
    general: LandCoverGeneral
    precipitation: Precipitation
    routing: Routing
    soilOrSediment: Dict[str, Any] = field(default_factory=dict)
    chemistry: Dict[str, Any] = field(default_factory=dict)
    buckets: List[LandCoverBucket]


@dataclass
class SubcatchmentIdentifier:
    name: str


@dataclass
class SubcatchmentGeneral:
    area: float = 10.0
    latitudeAtOutflow: float = 0.0
    longitudeAtOutflow: float = 0.3
    landCoverPercent: List[float]  # Percentages for different land covers


@dataclass
class SubcatchmentHydrology:
    rainfallMultiplier: float = 1.0
    snowfallMultiplier: float = 1.0
    snowfallTemperature: float = 0.0
    snowmeltTemperature: float = 0.0


@dataclass
class Subcatchment:
    identifier: SubcatchmentIdentifier
    general: SubcatchmentGeneral
    hydrology: SubcatchmentHydrology
    soilOrSediment: Dict[str, Any] = field(default_factory=dict)
    chemistry: Dict[str, Any] = field(default_factory=dict)
    landCovers: List[LandCover] = field(default_factory=list)


@dataclass
class ReachIdentifier:
    name: str


@dataclass
class ReachGeneral:
    length: float = 10000.0
    widthAtBottom: float = 10.0
    slope: float = 1e-04
    outflow: Optional[int] = None
    inflows: List[Optional[int]] = field(default_factory=list)


@dataclass
class Manning:
    a: float = 2.71
    b: float = 0.557
    c: float = 0.349
    f: float = 0.341
    n: float = 0.1


@dataclass
class ReachHydrology:
    hasAbstraction: bool = False
    hasEffluent: bool = False
    Manning: Manning
    initialFlow: float = 1.0


@dataclass
class Reach:
    identifier: ReachIdentifier
    general: ReachGeneral
    hydrology: ReachHydrology
    soilOrSediment: Dict[str, Any] = field(default_factory=dict)
    chemistry: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HRU:
    subcatchment: Subcatchment
    reach: Reach


@dataclass
class Catchment:
    name: str
    description: str = ""
    hrus: List[HRU] = field(default_factory=list)


@dataclass
class ParameterSet:
    general: General
    bucket: Bucket
    landCover: LandCover
    subcatchment: Subcatchment
    reach: Reach
