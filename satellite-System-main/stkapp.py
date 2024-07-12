#
import tkinter as tk
from PIL import Image, ImageTk
from agi.stk12.stkengine import STKEngine
from agi.stk12.stkobjects import *
from agi.stk12.stkutil import *
from agi.stk12.utilities.colors import *
from agi.stk12.stkengine.tkcontrols import GlobeControl, MapControl
from agi.stk12.utilities.exceptions import STKRuntimeError


class STKProTutorial:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("VCIS卫星仿真平台")

        try:
            self.stk = STKEngine.StartApplication(noGraphics=False)
            self.root = self.stk.NewObjectRoot()
        except STKRuntimeError as e:
            print(f"STK 启动失败: {e}")
            self.window.destroy()  # 关闭窗口并退出程序
            return

        # 创建标题框架
        self.titleFrame = tk.Frame(self.window)
        self.titleLabel = tk.Label(self.titleFrame, text="VCIS卫星仿真平台", font=("Arial", 24))
        self.titleLabel.pack()
        self.titleFrame.pack(side=tk.TOP, fill=tk.X, pady=10)

        self.mainFrame = tk.Frame(self.window)

        # 左侧按钮框架
        self.buttonFrame = tk.Frame(self.mainFrame)
        self.newScenarioBtn = tk.Button(self.buttonFrame, text="新建场景", width=15, command=self.newScenario)
        self.newScenarioBtn.pack(side=tk.TOP, pady=6)

        buttons = [
            ("创建设施", self.createFacilities),
            ("改变设施颜色", self.changeFacColor),
            ("创建目标", self.createTarget),
            ("创建船", self.createShip),
            ("创建卫星", self.createSatellites),
            ("设置航天飞机", self.shuttleContours),
            ("创建区域目标", self.createAreaTargets),
            ("连接", self.accessFunc),
            ("删除连接", self.removeAccess),
            ("创造传感器", self.createSensors),
            ("设置传感器可见性", self.sensorVisibility),
            ("自定义显示间隔", self.displayIntervals),
            ("访问显示间隔", self.accessIntervals),
            ("约束范围", self.rangeConstraint),
        ]

        for (text, command) in buttons:
            button = tk.Button(self.buttonFrame, text=text, width=15, wraplength=100, command=command)
            button.pack(side=tk.TOP, pady=6)
            button['state'] = "disabled"

        self.buttonFrame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # 控件框架（中间部分）
        self.controlFrame = tk.Frame(self.mainFrame)

        self.mapControl = MapControl(self.controlFrame, width=640, height=360)
        self.mapControl.pack(fill=tk.BOTH, expand=tk.YES, side=tk.RIGHT)

        self.globeControl = GlobeControl(self.controlFrame, width=640, height=360)
        self.globeControl.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)

        self.controlFrame.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)

        # 右侧空白区域
        self.rightFrame = tk.Frame(self.mainFrame, bg='white', width=640)
        self.rightFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

        # 加载图像并展示在右侧区域
        self.load_image('stkpython3.0/img/1.jpg')

        self.mainFrame.pack(fill=tk.BOTH, expand=tk.YES)
        self.window.mainloop()
    def load_image(self, image_path):
        img = Image.open(image_path)
        img = img.resize((320, 240), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        label = tk.Label(self.rightFrame, image=photo)
        label.image = photo  # 防止图片被垃圾回收
        label.pack()
    def run(self):
        self.window.mainloop()

    def destroy(self):
        self.root.CloseScenario()
        self.stk.ShutDown()
        self.window.destroy()

    def newScenario(self):
        self.root.NewScenario("ProTutorial")
        dimensions = self.root.UnitPreferences
        dimensions.ResetUnits()
        dimensions.SetCurrentUnit("DateFormat", "UTCG")
        scene = self.root.CurrentScenario

        scene.StartTime = "1 Jul 2002 00:00:00.00"
        scene.StopTime = "1 Jul 2002 04:00:00.00"
        scene.Epoch = "1 Jul 2002 00:00:00.00"

        dimensions.SetCurrentUnit("DistanceUnit", "km")
        dimensions.SetCurrentUnit("TimeUnit", "sec")
        dimensions.SetCurrentUnit("AngleUnit", "deg")
        dimensions.SetCurrentUnit("MassUnit", "kg")
        dimensions.SetCurrentUnit("PowerUnit", "dbw")
        dimensions.SetCurrentUnit("FrequencyUnit", "ghz")
        dimensions.SetCurrentUnit("SmallDistanceUnit", "m")
        dimensions.SetCurrentUnit("latitudeUnit", "deg")
        dimensions.SetCurrentUnit("longitudeunit", "deg")
        dimensions.SetCurrentUnit("DurationUnit", "HMS")
        dimensions.SetCurrentUnit("Temperature", "K")
        dimensions.SetCurrentUnit("SmallTimeUnit", "sec")
        dimensions.SetCurrentUnit("RatioUnit", "db")
        dimensions.SetCurrentUnit("rcsUnit", "dbsm")
        dimensions.SetCurrentUnit("DopplerVelocityUnit", "m/s")
        dimensions.SetCurrentUnit("Percent", "unitValue")
        self.newScenarioBtn['state'] = "disabled"
        self.createFacilitiesBtn['state'] = "normal"

    def createFacilities(self):
        self.baikonur = self.root.CurrentScenario.Children.New(AgESTKObjectType.eFacility, "Baikonur")
        self.baikonur.UseTerrain = False
        self.planetodetic = self.baikonur.Position.ConvertTo(AgEPositionType.ePlanetodetic)
        self.planetodetic.Lat = 48.0
        self.planetodetic.Lon = 55.0
        self.planetodetic.Alt = 0.0
        self.baikonur.Position.Assign(self.planetodetic)
        self.baikonur.ShortDescription = "Launch Site"
        self.baikonur.LongDescription = "Launch site in Kazakhstan. Also known as Tyuratam."

        self.perth = self.root.CurrentScenario.Children.New(AgESTKObjectType.eFacility, "Perth")
        self.perth.UseTerrain = False
        self.planetodetic = self.perth.Position.ConvertTo(AgEPositionType.ePlanetodetic)
        self.planetodetic.Lat = -31.0
        self.planetodetic.Lon = 116.0
        self.planetodetic.Alt = 0
        self.perth.Position.Assign(self.planetodetic)
        self.perth.ShortDescription = "Australian Tracking Station"

        self.wallops = self.root.CurrentScenario.Children.New(AgESTKObjectType.eFacility, "Wallops")
        self.wallops.UseTerrain = False
        self.planetodetic = self.wallops.Position.ConvertTo(AgEPositionType.ePlanetodetic)
        self.planetodetic.Lat = 37.8602
        self.planetodetic.Lon = -75.5095
        self.planetodetic.Alt = -0.0127878
        self.wallops.Position.Assign(self.planetodetic)
        self.wallops.ShortDescription = "NASA Launch Site/Tracking Station"

        result = self.root.ExecuteCommand("GetDirectory / Database Facility")
        facDataDir = result[0]
        filelocation = facDataDir + "\\stkFacility.fd"
        command = "ImportFromDB * Facility \"" + filelocation + "\"Class Facility SiteName \"Santiago Station AGO 3 STDN AGO3\" Network \"NASA NEN\" Rename Santiago"
        self.root.ExecuteCommand(command)
        command = "ImportFromDB * Facility \"" + filelocation + "\"Class Facility SiteName \"White Sands\" Network \"Other\" Rename WhiteSands"
        self.root.ExecuteCommand(command)

        self.santiago = self.root.CurrentScenario.Children["Santiago"]
        self.whitesands = self.root.CurrentScenario.Children["WhiteSands"]
        self.createFacilitiesBtn['state'] = "disabled"
        self.changeFacColorBtn['state'] = "normal"

    def changeFacColor(self):
        self.baikonur.Graphics.Color = Colors.Black
        self.perth.Graphics.Color = Colors.White
        self.wallops.Graphics.Color = Colors.Gray
        self.santiago.Graphics.Color = Colors.DarkGreen
        self.whitesands.Graphics.Color = Colors.LightSeaGreen
        self.changeFacColorBtn['state'] = "disabled"
        self.createTargetBtn['state'] = "normal"

    def createTarget(self):
        self.iceberg = self.root.CurrentScenario.Children.New(AgESTKObjectType.eTarget, "Iceberg")
        self.iceberg.UseTerrain = False
        self.planetodetic = self.iceberg.Position.ConvertTo(AgEPositionType.ePlanetodetic)
        self.planetodetic.Lat = 74.91
        self.planetodetic.Lon = -74.5
        self.planetodetic.Alt = 0.0

        self.iceberg.Position.Assign(self.planetodetic)
        self.iceberg.ShortDescription = "Only the tip."
        self.createTargetBtn['state'] = "disabled"
        self.createShipBtn['state'] = "normal"

    def addWaypoint(self, waypoints, Lat, Lon, Alt, Speed, tr):
        elem = waypoints.Add()
        elem.Latitude = Lat
        elem.Longitude = Lon
        elem.Altitude = Alt
        elem.Speed = Speed
        elem.TurnRadius = tr

    def createShip(self):
        cruise = self.root.CurrentScenario.Children.New(AgESTKObjectType.eShip, "Cruise")
        cruise.SetRouteType(AgEVePropagatorType.ePropagatorGreatArc)
        greatArc = cruise.Route
        interval = greatArc.EphemerisInterval
        interval.SetExplicitInterval("1 Jul 2002 00:00:00.00", interval.FindStopTime())
        greatArc.Method = AgEVeWayPtCompMethod.eDetermineTimeAccFromVel

        self.addWaypoint(greatArc.Waypoints, 44.1, -8.5, 0.0, .015, 0.0)
        self.addWaypoint(greatArc.Waypoints, 51.0, -26.6, 0.0, .015, 0.0)
        self.addWaypoint(greatArc.Waypoints, 52.1, -40.1, 0.0, .015, 0.0)
        self.addWaypoint(greatArc.Waypoints, 60.2, -55.0, 0.0, .015, 0.0)
        self.addWaypoint(greatArc.Waypoints, 68.2, -65.0, 0.0, .015, 0.0)
        self.addWaypoint(greatArc.Waypoints, 72.5, -70.1, 0.0, .015, 0.0)
        self.addWaypoint(greatArc.Waypoints, 74.9, -74.5, 0.0, .015, 0.0)

        cruise.SetAttitudeType(AgEVeAttitude.eAttitudeStandard)
        attitude = cruise.Attitude
        attitude.Basic.SetProfileType(AgEVeProfile.eProfileECFVelocityAlignmentWithRadialConstraint)
        cruise.Graphics.WaypointMarker.IsWaypointMarkersVisible = True
        cruise.Graphics.WaypointMarker.IsTurnMarkersVisible = True
        greatArc.Propagate()
        self.root.Rewind()
        self.createShipBtn['state'] = "disabled"
        self.createSatellitesBtn['state'] = "normal"

    def createSatellites(self):
        tdrs = self.root.CurrentScenario.Children.New(AgESTKObjectType.eSatellite, "TDRS")
        tdrs.SetPropagatorType(AgEVePropagatorType.ePropagatorTwoBody)
        twobody = tdrs.Propagator

        classical = twobody.InitialState.Representation.ConvertTo(AgEOrbitStateType.eOrbitStateClassical)
        classical.CoordinateSystemType = AgECoordinateSystem.eCoordinateSystemJ2000
        interval = twobody.EphemerisInterval
        interval.SetExplicitInterval("1 Jul 2002 00:00:00.000", "1 Jul 2002 04:00:00.000")
        twobody.Step = 60
        classical.LocationType = AgEClassicalLocation.eLocationTrueAnomaly
        trueAnomaly = classical.Location
        trueAnomaly.Value = 178.845262

        classical.SizeShapeType = AgEClassicalSizeShape.eSizeShapePeriod
        period = classical.SizeShape
        period.Eccentricity = 0.0
        period.Period = 86164.090540
        classical.Orientation.ArgOfPerigee = 0.0
        classical.Orientation.Inclination = 0.0
        classical.Orientation.AscNodeType = AgEOrientationAscNode.eAscNodeLAN
        lan = classical.Orientation.AscNode
        lan.Value = 259.999982
        twobody.InitialState.Representation.Assign(classical)
        twobody.Propagate()

        result = self.root.ExecuteCommand("GetDirectory / Database Satellite")
        satDataDir = result[0]
        filelocation = satDataDir + "\\stkSatDB.sd"
        command = "ImportFromDB * Satellite \"" + filelocation + "\" Rename TDRS_3 Propagate On CommonName \"TDRS 3\""
        self.root.ExecuteCommand(command)

        tdrsC = self.root.CurrentScenario.Children["TDRS_3"]
        sgp4 = tdrsC.Propagator
        interval = sgp4.EphemerisInterval
        interval.SetExplicitInterval("1 Jul 2002 00:00:00.000", "1 Jul 2002 04:00:00.000")

        self.ers1 = self.root.CurrentScenario.Children.New(AgESTKObjectType.eSatellite, "ERS1")
        self.ers1.SetPropagatorType(AgEVePropagatorType.ePropagatorJ4Perturbation)
        j4 = self.ers1.Propagator
        interval = j4.EphemerisInterval
        interval.SetExplicitInterval("1 Jul 2002 00:00:00.000", "1 Jul 2002 04:00:00.000")
        j4.Step = 60.00
        oOrb = j4.InitialState.Representation
        oOrb.Epoch = "1 Jul 2002 00:00:00.000"

        classical = j4.InitialState.Representation.ConvertTo(AgEOrbitStateType.eOrbitStateClassical)
        classical.CoordinateSystemType = AgECoordinateSystem.eCoordinateSystemJ2000
        classical.LocationType = AgEClassicalLocation.eLocationTrueAnomaly
        trueAnomaly = classical.Location
        trueAnomaly.Value = 0.0
        classical.SizeShapeType = AgEClassicalSizeShape.eSizeShapeSemimajorAxis
        semi = classical.SizeShape
        semi.SemiMajorAxis = 7163.14
        semi.Eccentricity = 0.0
        classical.Orientation.ArgOfPerigee = 0.0
        classical.Orientation.AscNodeType = AgEOrientationAscNode.eAscNodeLAN
        lan = classical.Orientation.AscNode
        lan.Value = 99.38
        classical.Orientation.Inclination = 98.50

        j4.InitialState.Representation.Assign(classical)
        j4.Propagate()
        self.root.Rewind()
        self.ers1.Graphics.Passes.VisibleSides = AgEVeGfxVisibleSides.eVisibleSidesDescending
        self.ers1.Graphics.Passes.VisibleSides = AgEVeGfxVisibleSides.eVisibleSidesBoth
        self.shuttle = self.root.CurrentScenario.Children.New(AgESTKObjectType.eSatellite, "Shuttle")
        self.shuttle.SetPropagatorType(AgEVePropagatorType.ePropagatorJ4Perturbation)
        j4 = self.shuttle.Propagator
        interval = j4.EphemerisInterval
        interval.SetExplicitInterval("1 Jul 2002 00:00:00.000", "1 Jul 2002 03:00:00.000")
        j4.Step = 60.00
        oOrb = j4.InitialState.Representation
        oOrb.Epoch = "1 Jul 2002 00:00:00.000"

        classical = j4.InitialState.Representation.ConvertTo(AgEOrbitStateType.eOrbitStateClassical)
        classical.CoordinateSystemType = AgECoordinateSystem.eCoordinateSystemJ2000
        classical.LocationType = AgEClassicalLocation.eLocationTrueAnomaly
        trueAnomaly = classical.Location
        trueAnomaly.Value = 0.0
        classical.SizeShapeType = AgEClassicalSizeShape.eSizeShapeAltitude
        altitude = classical.SizeShape
        altitude.ApogeeAltitude = 370.4
        altitude.PerigeeAltitude = 370.4
        classical.Orientation.ArgOfPerigee = 0.0
        classical.Orientation.AscNodeType = AgEOrientationAscNode.eAscNodeLAN
        lan = classical.Orientation.AscNode
        lan.Value = -151.0
        classical.Orientation.Inclination = 28.5
        j4.InitialState.Representation.Assign(classical)

        j4.Propagate()
        self.root.Rewind()
        self.createSatellitesBtn['state'] = "disabled"
        self.shuttleContoursBtn['state'] = "normal"

    def shuttleContours(self):
        self.shuttle.Graphics.SetAttributesType(AgEVeGfxAttributes.eAttributesBasic)
        orbitgfx = self.shuttle.Graphics.Attributes
        orbitgfx.Line.Style = AgELineStyle.eDashed
        orbitgfx.MarkerStyle = "Plus"

        contours = self.shuttle.Graphics.ElevContours
        elevations = contours.Elevations
        elevations.RemoveAll()
        elevations.AddLevelRange(0, 50, 10)

        for elem in elevations:
            elem.DistanceVisible = False
            elem.LineStyle = AgELineStyle.eDotDashed
            elem.LineWidth = AgELineWidth.e3

        contours.IsVisible = True
        self.root.Rewind()
        self.shuttleContoursBtn['state'] = "disabled"
        self.createAreaTargetsBtn['state'] = "normal"

    def createAreaTargets(self):
        self.searchArea = self.root.CurrentScenario.Children.New(AgESTKObjectType.eAreaTarget, "SearchArea")
        atGfx = self.searchArea.Graphics
        atGfx.MarkerStyle = "None"
        atGfx.Inherit = False
        atGfx.LabelVisible = False
        atGfx.CentroidVisible = False

        self.searchArea.AutoCentroid = False
        self.searchArea.AreaType = AgEAreaType.ePattern
        patterns = self.searchArea.AreaTypeData
        patterns.Add(78.4399, -77.6125)
        patterns.Add(77.7879, -71.1578)
        patterns.Add(74.5279, -69.0714)
        patterns.Add(71.6591, -69.1316)
        patterns.Add(70.0291, -70.8318)
        patterns.Add(71.9851, -76.3086)

        self.searchArea.UseTerrainData = False
        sphere = self.searchArea.Position.ConvertTo(AgEPositionType.eSpherical)
        sphere.Lat = 74.9533
        sphere.Lon = -74.5482
        sphere.Radius = 6358.186790
        self.searchArea.Position.Assign(sphere)
        self.createAreaTargetsBtn['state'] = "disabled"
        self.accessBtn['state'] = "normal"

    def accessFunc(self):
        self.access = self.ers1.GetAccessToObject(self.searchArea)
        self.access.ComputeAccess()
        self.root.Rewind()

        interval = self.access.DataProviders["Access Data"]
        result = interval.Exec("1 Jul 2002 00:00:00.000", "1 Jul 2002 04:00:00.000")
        self.accessBtn['state'] = "disabled"
        self.removeAccessBtn['state'] = "normal"

    def removeAccess(self):
        self.access.RemoveAccess()
        self.root.Rewind()
        self.removeAccessBtn['state'] = "disabled"
        self.createSensorsBtn['state'] = "normal"

    def createSensors(self):
        self.horizon = self.root.CurrentScenario.Children["ERS1"].Children.New(AgESTKObjectType.eSensor, "Horizon")
        self.horizon.SetPatternType(AgESnPattern.eSnSimpleConic)
        simpleConic = self.horizon.Pattern
        simpleConic.ConeAngle = 90
        self.horizon.SetPointingType(AgESnPointing.eSnPtFixed)
        fixedPt = self.horizon.Pointing
        azEl = fixedPt.Orientation.ConvertTo(AgEOrientationType.eAzEl)
        azEl.Elevation = 90
        azEl.AboutBoresight = AgEAzElAboutBoresight.eAzElAboutBoresightRotate
        fixedPt.Orientation.Assign(azEl)

        # removing the ers1 elevcontours from the 2d window
        self.ers1.Graphics.ElevContours.IsVisible = False
        downlink = self.root.CurrentScenario.Children["ERS1"].Children.New(AgESTKObjectType.eSensor, "Downlink")
        downlink.SetPatternType(AgESnPattern.eSnHalfPower)
        halfpower = downlink.Pattern
        halfpower.Frequency = .85
        halfpower.AntennaDiameter = 1.0

        downlink.SetPointingType(AgESnPointing.eSnPtTargeted)
        targeted = downlink.Pointing
        targeted.Boresight = AgESnPtTrgtBsightType.eSnPtTrgtBsightTracking
        targets = targeted.Targets
        targets.Add("Facility/Baikonur")
        targets.Add("Facility/WhiteSands")
        targets.Add("Facility/Perth")
        targets.AddObject(self.santiago)
        targets.Add(self.wallops.Path)

        self.root.Rewind()
        self.createSensorsBtn['state'] = "disabled"
        self.sensorVisibilityBtn['state'] = "normal"

    def sensorVisibility(self):
        fiveDegElev = self.root.CurrentScenario.Children["Wallops"].Children.New(AgESTKObjectType.eSensor,
                                                                                 "FiveDegElev")

        fiveDegElev.SetPatternType(AgESnPattern.eSnComplexConic)
        complexConic = fiveDegElev.Pattern
        complexConic.InnerConeHalfAngle = 0
        complexConic.OuterConeHalfAngle = 85
        complexConic.MinimumClockAngle = 0
        complexConic.MaximumClockAngle = 360

        fiveDegElev.SetPointingType(AgESnPointing.eSnPtFixed)
        fixedPt = fiveDegElev.Pointing
        azEl = fixedPt.Orientation.ConvertTo(AgEOrientationType.eAzEl)
        azEl.Elevation = 90
        azEl.AboutBoresight = AgEAzElAboutBoresight.eAzElAboutBoresightRotate
        fixedPt.Orientation.Assign(azEl)

        fiveDegElev.Graphics.Projection.DistanceType = AgESnProjectionDistanceType.eConstantAlt
        dispDistance = fiveDegElev.Graphics.Projection.DistanceData
        dispDistance.Max = 785.248
        dispDistance.Min = 0
        dispDistance.NumberOfSteps = 1
        self.root.Rewind()
        self.sensorVisibilityBtn['state'] = "disabled"
        self.displayIntervalsBtn['state'] = "normal"

    def displayIntervals(self):
        j4 = self.ers1.Propagator
        interval = j4.EphemerisInterval
        interval.SetExplicitInterval(interval.FindStartTime(), "2 Jul 2002 00:00:00.000")
        j4.Propagate()

        self.ers1.Graphics.SetAttributesType(AgEVeGfxAttributes.eAttributesCustom)
        customAtt = self.ers1.Graphics.Attributes
        gfxInterval = customAtt.Intervals.Add("1 Jul 2002 11:30:00.000", "1 Jul 2002 12:00:00.000")
        gfxInterval.GfxAttributes.Color = Colors.FromRGB(156, 49, 24)
        gfxInterval.GfxAttributes.IsVisible = True
        gfxInterval.GfxAttributes.Inherit = True

        gfxInterval = customAtt.Intervals.Add("1 Jul 2002 23:30:00.000", "1 Jul 2002 24:00:00.000")
        gfxInterval.GfxAttributes.Color = Colors.FromRGB(116, 80, 94)
        gfxInterval.GfxAttributes.IsVisible = True
        gfxInterval.GfxAttributes.Inherit = True
        self.root.Rewind()
        self.displayIntervalsBtn['state'] = "disabled"
        self.accessIntervalsBtn['state'] = "normal"

    def accessIntervals(self):
        self.ers1.Graphics.SetAttributesType(AgEVeGfxAttributes.eAttributesAccess)
        gfxAccess = self.ers1.Graphics.Attributes

        gfxAccess.AccessObjects.Add("Facility/Wallops")
        gfxAccess.AccessObjects.Add("Facility/Santiago")
        gfxAccess.AccessObjects.Add("Facility/Baikonur")
        gfxAccess.AccessObjects.Add("Facility/Perth")
        gfxAccess.AccessObjects.Add(self.whitesands.Path)

        orbitGfx = gfxAccess.NoAccess
        orbitGfx.IsVisible = True
        orbitGfx.Inherit = False
        orbitGfx.IsGroundMarkerVisible = False
        orbitGfx.IsOrbitMarkerVisible = False

        horizonDispTm = self.horizon
        horizonDispTm.SetDisplayStatusType(AgEDisplayTimesType.eDuringAccess)
        duringAccess = horizonDispTm.DisplayTimesData

        accessObjects = duringAccess.AccessObjects
        accessObjects.Add("Facility/Wallops")
        accessObjects.Add("Facility/Santiago")
        accessObjects.Add("Facility/Baikonur")
        accessObjects.AddObject(self.perth)
        accessObjects.Add(self.whitesands.Path)
        self.root.Rewind()
        self.accessIntervalsBtn['state'] = "disabled"
        self.rangeConstraintBtn['state'] = "normal"

    def rangeConstraint(self):
        access = self.horizon.GetAccessToObject(self.baikonur)
        access.ComputeAccess()
        minMax = self.horizon.AccessConstraints.AddConstraint(AgEAccessConstraints.eCstrRange)

        minMax.EnableMax = True
        minMax.Max = 2000
        minMax.Max = 1500
        minMax.Max = 1000
        minMax.Max = 500
        self.root.Rewind()
        self.rangeConstraintBtn['state'] = "disabled"


if __name__ == '__main__':
    stkProTutorial = STKProTutorial()
    stkProTutorial.run()