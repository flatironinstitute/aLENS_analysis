# trace generated using paraview version 5.11.1
# import paraview
# paraview.compatibility.major = 5
# paraview.compatibility.minor = 11

# import the simple module from the paraview
from paraview.simple import *
from pathlib import Path
import sys

# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

LoadPalette(paletteName="WhiteBackground")

if len(sys.argv) == 1:
    work_dir = Path.cwd()
else:
    work_dir = Path(sys.argv[1])

assert work_dir.exists()

# create a new 'PVD Reader'
sylinderpvtppvd = PVDReader(
    registrationName="Sylinderpvtp.pvd",
    FileName=str(work_dir / "result/Sylinderpvtp.pvd"),
)
sylinderpvtppvd.CellArrays = [
    "gid",
    "group",
    "isImmovable",
    "radius",
    "radiusCollision",
    "length",
    "lengthCollision",
    "vel",
    "omega",
    "velCollision",
    "omegaCollision",
    "velBilateral",
    "omegaBilateral",
    "velNonBrown",
    "omegaNonBrown",
    "force",
    "torque",
    "forceCollision",
    "torqueCollision",
    "forceBilateral",
    "torqueBilateral",
    "forceNonBrown",
    "torqueNonBrown",
    "velBrown",
    "omegaBrown",
    "xnorm",
    "znorm",
]
sylinderpvtppvd.PointArrays = ["endLabel"]

# get animation scene
animationScene1 = GetAnimationScene()

# get the time-keeper
timeKeeper1 = GetTimeKeeper()

# get active view
renderView1 = GetActiveViewOrCreate("RenderView")
# get the material library
materialLibrary1 = GetMaterialLibrary()

# get display properties
sylinderpvtppvdDisplay = GetDisplayProperties(sylinderpvtppvd, view=renderView1)

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# create a new 'PVD Reader'
proteinpvtppvd = PVDReader(
    registrationName="Proteinpvtp.pvd",
    FileName=str(work_dir / "result/Proteinpvtp.pvd"),
)
proteinpvtppvd.CellArrays = ["gid", "tag"]
proteinpvtppvd.PointArrays = ["idBind"]

# create a new 'PVD Reader'
conBlockpvtppvd = PVDReader(
    registrationName="ConBlockpvtp.pvd",
    FileName=str(work_dir / "result/ConBlockpvtp.pvd"),
)
conBlockpvtppvd.CellArrays = [
    "oneSide",
    "bilateral",
    "delta0",
    "gamma",
    "kappa",
    "Stress",
]
conBlockpvtppvd.PointArrays = [
    "gid",
    "globalIndex",
    "unscaledForceComIJ",
    "unscaledTorqueComIJ",
]

# show data in view
conBlockpvtppvdDisplay = Show(conBlockpvtppvd, renderView1, "GeometryRepresentation")

# trace defaults for the display properties.
conBlockpvtppvdDisplay.Representation = "Surface"
conBlockpvtppvdDisplay.ColorArrayName = [None, ""]
conBlockpvtppvdDisplay.SelectTCoordArray = "None"
conBlockpvtppvdDisplay.SelectNormalArray = "None"
conBlockpvtppvdDisplay.SelectTangentArray = "None"
conBlockpvtppvdDisplay.OSPRayScaleArray = "gid"
conBlockpvtppvdDisplay.OSPRayScaleFunction = "PiecewiseFunction"
conBlockpvtppvdDisplay.SelectOrientationVectors = "None"
conBlockpvtppvdDisplay.ScaleFactor = 0.49968750000000006
conBlockpvtppvdDisplay.SelectScaleArray = "None"
conBlockpvtppvdDisplay.GlyphType = "Arrow"
conBlockpvtppvdDisplay.GlyphTableIndexArray = "None"
conBlockpvtppvdDisplay.GaussianRadius = 0.024984375000000003
conBlockpvtppvdDisplay.SetScaleArray = ["POINTS", "gid"]
conBlockpvtppvdDisplay.ScaleTransferFunction = "PiecewiseFunction"
conBlockpvtppvdDisplay.OpacityArray = ["POINTS", "gid"]
conBlockpvtppvdDisplay.OpacityTransferFunction = "PiecewiseFunction"
conBlockpvtppvdDisplay.DataAxesGrid = "GridAxesRepresentation"
conBlockpvtppvdDisplay.PolarAxes = "PolarAxesRepresentation"
conBlockpvtppvdDisplay.SelectInputVectors = ["POINTS", "unscaledForceComIJ"]
conBlockpvtppvdDisplay.WriteLog = ""

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
conBlockpvtppvdDisplay.OSPRayScaleFunction.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    920.3745727539062,
    0.30000001192092896,
    0.5,
    0.0,
    4095.0,
    1.0,
    0.5,
    0.0,
]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
conBlockpvtppvdDisplay.ScaleTransferFunction.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    359.38435698009675,
    0.30000001192092896,
    0.5,
    0.0,
    1599.0,
    1.0,
    0.5,
    0.0,
]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
conBlockpvtppvdDisplay.OpacityTransferFunction.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    359.38435698009675,
    0.30000001192092896,
    0.5,
    0.0,
    1599.0,
    1.0,
    0.5,
    0.0,
]

# show data in view
proteinpvtppvdDisplay = Show(proteinpvtppvd, renderView1, "GeometryRepresentation")

# trace defaults for the display properties.
proteinpvtppvdDisplay.Representation = "Surface"
proteinpvtppvdDisplay.ColorArrayName = [None, ""]
proteinpvtppvdDisplay.SelectTCoordArray = "None"
proteinpvtppvdDisplay.SelectNormalArray = "None"
proteinpvtppvdDisplay.SelectTangentArray = "None"
proteinpvtppvdDisplay.OSPRayScaleArray = "idBind"
proteinpvtppvdDisplay.OSPRayScaleFunction = "PiecewiseFunction"
proteinpvtppvdDisplay.SelectOrientationVectors = "None"
proteinpvtppvdDisplay.ScaleFactor = 0.49968750000000006
proteinpvtppvdDisplay.SelectScaleArray = "None"
proteinpvtppvdDisplay.GlyphType = "Arrow"
proteinpvtppvdDisplay.GlyphTableIndexArray = "None"
proteinpvtppvdDisplay.GaussianRadius = 0.024984375000000003
proteinpvtppvdDisplay.SetScaleArray = ["POINTS", "idBind"]
proteinpvtppvdDisplay.ScaleTransferFunction = "PiecewiseFunction"
proteinpvtppvdDisplay.OpacityArray = ["POINTS", "idBind"]
proteinpvtppvdDisplay.OpacityTransferFunction = "PiecewiseFunction"
proteinpvtppvdDisplay.DataAxesGrid = "GridAxesRepresentation"
proteinpvtppvdDisplay.PolarAxes = "PolarAxesRepresentation"
proteinpvtppvdDisplay.SelectInputVectors = [None, ""]
proteinpvtppvdDisplay.WriteLog = ""

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
proteinpvtppvdDisplay.OSPRayScaleFunction.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    920.3745727539062,
    0.30000001192092896,
    0.5,
    0.0,
    4095.0,
    1.0,
    0.5,
    0.0,
]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
proteinpvtppvdDisplay.ScaleTransferFunction.Points = [
    -1.0,
    0.0,
    0.5,
    0.0,
    358.60911267551893,
    0.30000001192092896,
    0.5,
    0.0,
    1599.0,
    1.0,
    0.5,
    0.0,
]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
proteinpvtppvdDisplay.OpacityTransferFunction.Points = [
    -1.0,
    0.0,
    0.5,
    0.0,
    358.60911267551893,
    0.30000001192092896,
    0.5,
    0.0,
    1599.0,
    1.0,
    0.5,
    0.0,
]

# update the view to ensure updated data information
renderView1.Update()

tube1 = Tube(registrationName="Tube1", Input=proteinpvtppvd)
tube1.Scalars = ["POINTS", "idBind"]
tube1.Vectors = ["POINTS", "1"]
tube1.Radius = 0.0025


# show data in view
tube1Display = Show(tube1, renderView1, "GeometryRepresentation")

# trace defaults for the display properties.
tube1Display.Representation = "Surface"
tube1Display.ColorArrayName = [None, ""]
tube1Display.SelectTCoordArray = "None"
tube1Display.SelectNormalArray = "None"
tube1Display.SelectTangentArray = "None"
tube1Display.OSPRayScaleFunction = "PiecewiseFunction"
tube1Display.SelectOrientationVectors = "None"
tube1Display.ScaleFactor = -2.0000000000000002e298
tube1Display.SelectScaleArray = "None"
tube1Display.GlyphType = "Arrow"
tube1Display.GlyphTableIndexArray = "None"
tube1Display.GaussianRadius = -1e297
tube1Display.SetScaleArray = [None, ""]
tube1Display.ScaleTransferFunction = "PiecewiseFunction"
tube1Display.OpacityArray = [None, ""]
tube1Display.OpacityTransferFunction = "PiecewiseFunction"
tube1Display.DataAxesGrid = "GridAxesRepresentation"
tube1Display.PolarAxes = "PolarAxesRepresentation"
tube1Display.SelectInputVectors = [None, ""]
tube1Display.WriteLog = ""

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
tube1Display.OSPRayScaleFunction.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    920.3745727539062,
    0.30000001192092896,
    0.5,
    0.0,
    4095.0,
    1.0,
    0.5,
    0.0,
]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
tube1Display.ScaleTransferFunction.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    0.22475569542219934,
    0.30000001192092896,
    0.5,
    0.0,
    1.0,
    1.0,
    0.5,
    0.0,
]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
tube1Display.OpacityTransferFunction.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    0.22475569542219934,
    0.30000001192092896,
    0.5,
    0.0,
    1.0,
    1.0,
    0.5,
    0.0,
]


# change solid color
tube1Display.AmbientColor = [0.6666666666666666, 0.0, 1.0]
tube1Display.DiffuseColor = [0.6666666666666666, 0.0, 1.0]

renderView1.Background = [1.0, 1.0, 1.0]  # Set background to white
renderView1.Update()

# update the view to ensure updated data information
renderView1.Update()

# set active source
SetActiveSource(sylinderpvtppvd)

# create a new 'Glyph'
glyph1 = Glyph(registrationName="gid", Input=sylinderpvtppvd, GlyphType="Sphere")
glyph1.OrientationArray = ["POINTS", "No orientation array"]
glyph1.ScaleArray = ["POINTS", "No scale array"]
glyph1.ScaleFactor = 0.49968750000000006
glyph1.GlyphTransform = "Transform2"
glyph1.GlyphType.ThetaResolution = 16
glyph1.GlyphType.PhiResolution = 16

# show data in view
glyph1Display = Show(glyph1, renderView1, "GeometryRepresentation")

# trace defaults for the display properties.
glyph1Display.Representation = "Surface"
glyph1Display.ColorArrayName = [None, ""]
glyph1Display.SelectTCoordArray = "None"
glyph1Display.SelectNormalArray = "None"
glyph1Display.SelectTangentArray = "None"
glyph1Display.OSPRayScaleArray = "endLabel"
glyph1Display.OSPRayScaleFunction = "PiecewiseFunction"
glyph1Display.SelectOrientationVectors = "None"
glyph1Display.ScaleFactor = 0.5496562480926513
glyph1Display.SelectScaleArray = "None"
glyph1Display.GlyphType = "Sphere"
glyph1Display.GlyphTableIndexArray = "None"
glyph1Display.GaussianRadius = 0.02748281240463257
glyph1Display.SetScaleArray = ["POINTS", "endLabel"]
glyph1Display.ScaleTransferFunction = "PiecewiseFunction"
glyph1Display.OpacityArray = ["POINTS", "endLabel"]
glyph1Display.OpacityTransferFunction = "PiecewiseFunction"
glyph1Display.DataAxesGrid = "GridAxesRepresentation"
glyph1Display.PolarAxes = "PolarAxesRepresentation"
glyph1Display.SelectInputVectors = [None, ""]
glyph1Display.WriteLog = ""

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
glyph1Display.OSPRayScaleFunction.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    920.3745727539062,
    0.30000001192092896,
    0.5,
    0.0,
    4095.0,
    1.0,
    0.5,
    0.0,
]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
glyph1Display.ScaleTransferFunction.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    0.22475569542219934,
    0.30000001192092896,
    0.5,
    0.0,
    1.0,
    1.0,
    0.5,
    0.0,
]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
glyph1Display.OpacityTransferFunction.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    0.22475569542219934,
    0.30000001192092896,
    0.5,
    0.0,
    1.0,
    1.0,
    0.5,
    0.0,
]

# update the view to ensure updated data information
renderView1.Update()

# Properties modified on glyph1
glyph1.GlyphType = "Sphere"

# update the view to ensure updated data information
renderView1.Update()

# Properties modified on glyph1
glyph1.ScaleArray = ["CELLS", "radius"]


# update the view to ensure updated data information
renderView1.Update()

# Properties modified on glyph1
glyph1.ScaleFactor = 2.0

# update the view to ensure updated data information
renderView1.Update()

# Properties modified on glyph1
glyph1.GlyphMode = "All Points"

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(glyph1Display, ("POINTS", "gid"))

# rescale color and/or opacity maps used to include current data range
glyph1Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, True)

# get 2D transfer function for 'gid'
gidTF2D = GetTransferFunction2D("gid")

# get color transfer function/color map for 'gid'
gidLUT = GetColorTransferFunction("gid")
gidLUT.TransferFunction2D = gidTF2D
gidLUT.RGBPoints = [
    0.0,
    0.0,
    0.0,
    0.8,
    361.9714285714286,
    0.0,
    0.0,
    0.8,
    1237.0285714285715,
    0.8,
    0.3,
    0.3,
    1599.0,
    0.0,
    0.695201,
    0.5,
]
gidLUT.ColorSpace = "Step"
gidLUT.NanColor = [0.803922, 0.0, 0.803922]
gidLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'gid'
gidPWF = GetOpacityTransferFunction("gid")
gidPWF.Points = [
    0.0,
    0.0,
    0.5,
    0.0,
    359.38435698009675,
    0.30000001192092896,
    0.5,
    0.0,
    1599.0,
    1.0,
    0.5,
    0.0,
]
gidPWF.ScalarRangeInitialized = 1

# Apply a preset using its name. Note this may not work as expected when
# presets have duplicate names.
gidLUT.ApplyPreset("Rainbow Uniform", True)
gidLUT.InvertTransferFunction()

# hide color bar/color legend
glyph1Display.SetScalarBarVisibility(renderView1, False)

# rename source object
# RenameSource('gid', glyph1)


# hide data in view
Hide(proteinpvtppvd, renderView1)

# hide data in view
Hide(conBlockpvtppvd, renderView1)

# hide data in view
Hide(sylinderpvtppvd, renderView1)

# ================================================================
# addendum: following script captures some of the application
# state to faithfully reproduce the visualization during playback
# ================================================================

# get layout
layout1 = GetLayout()

# --------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels

layout1.PreviewMode = [3840, 2160]
layout1.SetSize(3840, 2159)

renderView1.Background = [1.0, 1.0, 1.0]  # Set background to white
renderView1.Update()

renderView1.ResetCamera(True)

# -----------------------------------
# saving camera placements for views

# current camera placement for renderView1
# renderView1.CameraPosition = [-0.0015624999999999112, 0.11405147342675738, 9.73327946023483]
# renderView1.CameraFocalPoint = [-0.0015624999999999112, 0.11405147342675738, 0.04801966631384255]
# renderView1.CameraParallelScale = 2.5067296914324664

# --------------------------------------------
# uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).
animationScene1 = GetAnimationScene()
if len(sys.argv) == 3:
    animationScene1.AnimationTime = float(sys.argv[2])
    SaveScreenshot(
        str(work_dir / f"snapshot_chromatin_{int(sys.argv[2])}.png"),
        renderView1,
    )
else:
    animationScene1.GoToLast()
    SaveScreenshot(
        str(work_dir / f"snapshot_chromatin_last.png"),
        renderView1,
    )
