#pylint: disable=no-self-use, fixme
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

from ..loadUiType import QMenu, QAction, QFileDialog, toPyObject, Qt, QInputDialog
from ..mayaInterface import disconnected
from ..constants import THING_ROLE, C_SHAPE_TYPE, S_SLIDER_TYPE

# Registration class
class ToolActions(object):
	def __init__(self, window, system=None):
		self.system = system
		self.window = window

		# Build Actions
		blendToTargetACT = QAction("Blend To Target", window)
		generateShapeIncrementalsACT = QAction("Generate Shape Incrementals", window)
		#generateTimeIncrementalsACT = QAction("Generate Time Incrementals", window)
		relaxToSelectionACT = QAction("Relax To Selection", window)
		snapShapeToNeutralACT = QAction("Snap Shape To Neutral", window)
		softSelectToClusterACT = QAction("Soft Select To Cluster", window)
		extractDeltasACT = QAction("Extract Deltas", window)
		applyDeltasACT = QAction("Apply Deltas", window)
		extractExternalACT = QAction("Extract External", window)
		tweakMixACT = QAction("Tweak Mix", window)
		extractProgressivesACT = QAction("Extract Progressive", window)

		# Build the menu
		menu = QMenu("Tools")
		menu.addAction(blendToTargetACT)
		menu.addAction(generateShapeIncrementalsACT)
		#menu.addAction(generateTimeIncrementalsACT)
		menu.addAction(relaxToSelectionACT)
		menu.addAction(snapShapeToNeutralACT)
		menu.addAction(softSelectToClusterACT)
		menu.addSeparator()
		menu.addAction(extractDeltasACT)
		menu.addAction(applyDeltasACT)
		menu.addAction(extractExternalACT)
		menu.addAction(tweakMixACT)
		menu.addAction(extractProgressivesACT)

		# Set up the connections
		blendToTargetACT.triggered.connect(self.blendToTarget)
		generateShapeIncrementalsACT.triggered.connect(self.generateShapeIncrementals)
		#generateTimeIncrementalsACT.triggered.connect(self.generateTimeIncrementals)
		relaxToSelectionACT.triggered.connect(self.relaxToSelection)
		snapShapeToNeutralACT.triggered.connect(self.snapShapeToNeutral)
		softSelectToClusterACT.triggered.connect(self.softSelectToCluster)
		extractDeltasACT.triggered.connect(self.extractDeltas)
		applyDeltasACT.triggered.connect(self.applyDeltas)
		extractExternalACT.triggered.connect(self.extractExternal)
		tweakMixACT.triggered.connect(self.tweakMix)
		extractProgressivesACT.triggered.connect(self.extractProgressives)

		mbar = window.menuBar
		mbar.addMenu(menu)

	def blendToTarget(self):
		sel = cmds.ls(sl=True)
		if len(sel) >= 2:
			blendToTarget(sel[0], sel[1])

	def applyDeltas(self):
		if not self.system:
			return
		sel = cmds.ls(sl=True)
		restShape = self.system.simplex.buildRestShape()
		rest = self.system.extractShape(restShape, live=False, offset=0.0)
		if len(sel) >= 2:
			applyDeltas(sel[0], sel[1], rest)
		cmds.delete(rest)

	def extractDeltas(self):
		if not self.system:
			return
		sel = cmds.ls(sl=True)
		restShape = self.system.simplex.buildRestShape()
		rest = self.system.extractShape(restShape, live=False, offset=0.0)
		if len(sel) >= 2:
			extractDeltas(sel[0], sel[1], rest)
		cmds.delete(rest)

	def generateShapeIncrementals(self):
		sel = cmds.ls(sl=True)[0]
		if len(sel) >= 2:
			# TODO, build a UI for this
			increments = QInputDialog.getInt(self.window, "Increments", "Number of Increments", 4, 1, 100)
			if increments is None:
				return
			generateShapeIncrementals(sel[0], sel[1], increments)

	def generateTimeIncrementals(self):
		# TODO, build a UI for this
		increments = 4
		startFrame = 0
		endFrame = 12
		sel = cmds.ls(sl=True)[0]
		name = sel
		generateTimeIncrementals(name, sel, startFrame, endFrame, increments)

	def relaxToSelection(self):
		sel = cmds.ls(sl=True)
		if len(sel) >= 2:
			relaxToSelection(sel[0], sel[1])

	def snapShapeToNeutral(self):
		sel = cmds.ls(sl=True)
		if len(sel) >= 2:
			snapShapeToNeutral(sel[0], sel[1])
		elif len(sel) == 1:
			restShape = self.system.simplex.buildRestShape()
			rest = self.system.extractShape(restShape, live=False, offset=0.0)
			snapShapeToNeutral(sel[0], rest)
			cmds.delete(rest)

	def softSelectToCluster(self):
		sel = cmds.ls(sl=True, objectsOnly=True)
		if sel:
			softSelectToCluster(sel[0], "{0}_Soft".format(sel[0]))

	def extractExternal(self):
		sel = cmds.ls(sl=True)
		path, fliter = QFileDialog.getSaveFileName(self.window, "Extract External", "", "Simplex (*.smpx)")
		if sel and path:
			extractExternal(self.system, sel[0], path)

	def tweakMix(self):
		if not self.system:
			return
		live = self.window.uiLiveShapeConnectionACT.isChecked()

		comboIndexes = self.window.getFilteredChildSelection(self.window.uiComboTREE, C_SHAPE_TYPE)
		comboShapes = []
		for i in comboIndexes:
			if not i.isValid():
				continue
			progPair = toPyObject(i.model().data(i, THING_ROLE))
			combo = progPair.prog.parent
			if not progPair.shape.isRest:
				comboShapes.append((combo, progPair.shape))

		tweakMix(self.system, comboShapes, live)

	def extractProgressives(self):
		if not self.system:
			return
		live = self.window.uiLiveShapeConnectionACT.isChecked()

		sliderIndexes = self.window.getFilteredChildSelection(self.window.uiSliderTREE, S_SLIDER_TYPE)
		sliders = []
		for i in sliderIndexes:
			if not i.isValid():
				continue
			slider = toPyObject(i.model().data(i, THING_ROLE))
			sliders.append(slider)
		extractProgressives(self.system, sliders, live)

########################################################################################################
# actual tools
def blendToTarget(source, target):
	''' Quickly blend one object to another '''
	blendAr = cmds.blendShape(source, target)[0]
	cmds.blendShape(blendAr, edit=True, weight=((0, 1)))

def applyDeltas(deltaMesh, targetMesh, rest):
	'''
	Apply the extracted deltas from `extractDeltas` to another object
	'''
	# Create a temporary mesh to hold the sum of the delta and our target
	outputMesh = cmds.duplicate(rest, name='deltaMesh')

	# create that 'sum', and delete the history
	blendNode = cmds.blendShape(deltaMesh, targetMesh, outputMesh)[0]
	cmds.blendShape(blendNode, edit=True, weight=((0, 1), (1, 1)))
	cmds.delete(outputMesh, constructionHistory=True)

	# Connect that 'sum' back into our target, and delete the temp mesh
	cmds.blendShape(outputMesh, targetMesh)
	cmds.delete(outputMesh)

def extractDeltas(original, sculpted, rest):
	'''
	Get the difference between the original and the sculpted meshes
	Then apply that difference to the rest
	'''
	extractedDeltas = cmds.duplicate(rest, name="extractedDeltas")[0]
	deltaBlends = cmds.blendShape(sculpted, original, extractedDeltas)
	cmds.blendShape(deltaBlends, edit=True, weight=((0, 1), (1, -1)))

def generateShapeIncrementals(startObj, endObj, increments):
	'''
	Pick a start object, then an end object, and define a number of incremental steps
	'''
	shapeDup = cmds.duplicate(endObj, name="shapeDup")
	bs = cmds.blendShape(startObj, shapeDup)

	for i in range(1, increments):
		val = float(increments - i) / increments
		percent = int(float(i) * 100 /increments)
		cmds.blendShape(bs, edit=True, weight=((0, val)))
		cmds.duplicate(shapeDup, name="{0}_{1}".format(endObj, percent))

	cmds.delete(shapeDup)
	cmds.select(endObj)

def generateTimeIncrementals(name, thing, startFrame, endFrame, increments):
	'''
	pick an animated object
	pick the endframe
	pick the number of increments
	pick the name for the results
	'''
	cmds.currentTime(startFrame)
	for i in range(1, increments):
		val = float(i) / increments
		percent = int(val * 100)
		newFrame = float(i * (endFrame - startFrame)) / increments
		cmds.currentTime(newFrame)
		nn = "{0}_{1}".format(name, percent)
		cmds.duplicate(thing, name=nn)

	cmds.currentTime(startFrame)
	cmds.select(thing)

def relaxToSelection(source, target):
	'''
	Transfer high-frequency sculpts (like wrinkles) from one shape to another

	This sets up a delta mush on a detailed mesh (source) before blending to a
	less detailed shape (target). Turning up the deltaMush re-applies the
	high-resolution deltas to that less detailed shape so then blend it back
	into the target
	'''
	sourceDup = cmds.duplicate(source, name="deltaMushMesh")[0]
	targetDup = cmds.duplicate(target, name="targetDup")[0]
	deltaMushRelax = cmds.group(sourceDup, name="deltaMushRelax")
	cmds.hide([sourceDup, targetDup, deltaMushRelax])

	cmds.addAttr(deltaMushRelax, longName="smooth_iter", attributeType="long", minValue=0, maxValue=100, defaultValue=10)
	smoothIter = "{0}.smooth_iter".format(deltaMushRelax)
	cmds.setAttr(smoothIter, edit=True, keyable=True)

	blender = cmds.blendShape(targetDup, sourceDup)
	deltaMush = cmds.deltaMush(sourceDup, smoothingIterations=10, smoothingStep=0.5, pinBorderVertices=1, envelope=1)[0]
	cmds.connectAttr(smoothIter, deltaMush+".smoothingIterations", force=True)

	cmds.delete(targetDup)
	finalBlend = cmds.blendShape(sourceDup, target)
	cmds.blendShape(finalBlend, edit=True, weight=((0, 1)))
	cmds.blendShape(blender, edit=True, weight=((0, 1)))

	cmds.select(deltaMushRelax)

def snapShapeToNeutral(source, target):
	'''
	Take a mesh, and find the closest location on the target head, and snap to that
	Then set up a blendShape so the artist can "paint" in the snapping behavior
	'''
	# Make a duplicate of the source and snap it to the target
	snapShape = cmds.duplicate(source, name='snp')
	cmds.transferAttributes(
		target, snapShape,
		transferPositions=1,
		sampleSpace=1, # 0=World, 1=Local, 3=UV
		searchMethod=0, # 0=Along Normal, 1=Closest Location
	)

	# Then delete history
	cmds.delete(snapShape, constructionHistory=True)
	cmds.hide(snapShape)

	# Blend the source to the snappedShape
	bs = cmds.blendShape(snapShape, source)[0]
	cmds.blendShape(bs, edit=True, weight=((0, 1)))

	# But set the weights back to 0.0 for painting
	numVerts = cmds.polyEvaluate(source, vertex=1)
	setter = '{0}.inputTarget[0].inputTargetGroup[0].targetWeights[0:{1}]'.format(bs, numVerts-1)
	weights = [0.0] * numVerts
	cmds.setAttr(setter, *weights, size=numVerts)

def softSelectToCluster(mesh, name):
	# Get the manipulator position for the selection
	cmds.setToolTo('Move')
	currentMoveMode = cmds.manipMoveContext('Move', query=True, mode=True) #Get the original mode
	cmds.manipMoveContext('Move', edit=True, mode=0) #set to the correct mode
	pos = cmds.manipMoveContext('Move', query=True, position=True) # get the position
	cmds.manipMoveContext('Move', edit=True, mode=currentMoveMode) # and reset

	# Grab the soft selection values using the API
	selection = om.MSelectionList()
	ssel = om.MRichSelection()
	ssel.getSelection(selection)

	dagPath = om.MDagPath()
	component = om.MObject()

	vertIter = om.MItSelectionList(selection, om.MFn.kMeshVertComponent)
	elements, weights = [], []

	# TODO Be a bit more explicit here with the mesh, its shapeNode, and the dagPath
	# so we can make sure we don't have multiple meshes with verts selected

	softSel = {}
	while not vertIter.isDone():
		vertIter.getDagPath(dagPath, component)
		dagPath.pop() #Grab the parent of the shape node
		node = dagPath.fullPathName()
		fnComp = om.MFnSingleIndexedComponent(component)
		getWeight = lambda i: fnComp.weight(i).influence() if fnComp.hasWeights() else 1.0

		for i in range(fnComp.elementCount()):
			softSel[fnComp.element(i)] = getWeight(i)
		vertIter.next()

	if not softSel:
		print "No Soft Selection"
		return

	# Build the Cluster and set the weights
	clusterNode, clusterHandle = cmds.cluster(mesh, name=name)
	vnum = cmds.polyEvaluate(mesh, vertex=1)
	weights = [softSel.get(i, 0.0) for i in range(vnum)]
	cmds.setAttr('{0}.weightList[0].weights[0:{1}]'.format(clusterNode, vnum-1), *weights, size=vnum)

	# Reposition the cluster
	cmds.xform(clusterHandle, a=True, ws=True, piv=(pos[0], pos[1], pos[2]))
	clusterShape = cmds.listRelatives(clusterHandle, c=True, s=True)
	cmds.setAttr(clusterShape[0] + '.origin', pos[0], pos[1], pos[2])

def extractExternal(system, mesh, path):
	print "SYSTEM", system
	system.extractExternal(path, mesh)

def tweakMix(system, comboShapes, live):
	# first extract the rest shape non-live
	restGeo = system.extractShape(system.simplex.restShape, live=False, offset=0)

	floatShapes = system.simplex.getFloatingShapes()
	floatShapes = [i.thing for i in floatShapes]

	offset = 5
	for combo, shape in comboShapes:
		offset += 5
		geo = system.extractComboShape(combo, shape, live=live, offset=offset)
		# disconnect the controller from the operator
		tweakShapes = []
		with disconnected(system.DCC.op) as sliderCnx:
			# disconnect any float shapes
			with disconnected(floatShapes):
				# zero all slider vals on the op
				for a in sliderCnx.itervalues():
					cmds.setAttr(a, 0.0)

				# set the combo values
				sliderVals = []
				for pair in combo.pairs:
					cmds.setAttr(sliderCnx[pair.slider.thing], pair.value)

				for shape in system.simplex.shapes[1:]: #skip the restShape
					shapeVal = cmds.getAttr(shape.thing)
					if shapeVal != 0.0: # maybe handle floating point errors
						tweakShapes.append((shape, shapeVal))

		tweakMeshes = []
		with disconnected(system.DCC.shapeNode) as shapeCnx:
			for a in shapeCnx.itervalues():
				cmds.setAttr(a, 0.0)
			for tshape, shapeVal in tweakShapes:
				cmds.setAttr(tshape.thing, shapeVal)
				#print "setAttr", tshape.thing, shapeVal
				tweakMesh = cmds.duplicate(system.DCC.mesh, name='{0}_Tweak'.format(tshape.name))[0]
				tweakMeshes.append(tweakMesh)
				cmds.setAttr(tshape.thing, 0.0)

		# Yeah, yeah, this is REALLY ugly, but it's quick and it works
		tempBS = cmds.blendShape(geo, name='Temp_BS')
		cmds.blendShape(tempBS, edit=True, target=(geo, 0, restGeo, 1.0))
		cmds.blendShape(tempBS, edit=True, weight=[(0, 1.0)])
		cmds.delete(geo, constructionHistory=True)

		# build the actual blendshape
		tweakBS = cmds.blendShape(geo, name="Tweak_BS")
		for i, tm in enumerate(tweakMeshes):
			cmds.blendShape(tweakBS, edit=True, target=(geo, i, tm, 1.0))
		tmLen = len(tweakMeshes)
		cmds.blendShape(tweakBS, edit=True, weight=zip(range(tmLen), [1.0]*tmLen))

		cmds.delete(tweakMeshes)
		cmds.delete(restGeo)

def extractProgressives(system, sliders, live):
	for slider in sliders:
		system.extractProgressive(slider, live, 10.0)

