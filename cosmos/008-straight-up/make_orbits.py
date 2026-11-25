"""Original KOSMION spatial orbit illustrations; compressed sizes and time, not flight ephemerides."""
import bpy,math,sys,pathlib,random,json,urllib.request
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];mode=args[0] if args else 'orbit';pilot='--pilot' in args;out=R/'original3d'/mode;out.mkdir(parents=True,exist_ok=True);tex=R/'textures';tex.mkdir(exist_ok=True)
url='https://raw.githubusercontent.com/NASAWorldWind/WorldWindJava/master/src/images/BMNG_world.topo.bathy.200405.3.2048x1024.jpg';earthfile=tex/'earth.png'
if not earthfile.exists():
 with urllib.request.urlopen(url,timeout=90) as a:earthfile.write_bytes(a.read())
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
try:s.render.engine='BLENDER_EEVEE_NEXT'
except:s.render.engine='BLENDER_EEVEE'
if hasattr(s,'eevee'):s.eevee.taa_render_samples=24
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50 if pilot else 100;s.render.fps=25;s.frame_start=1;s.frame_end=1000;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=96;s.render.film_transparent=False
s.world=bpy.data.worlds.new('Deep space');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.003,.005,.009,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.15
try:s.view_settings.view_transform='AgX'
except:pass
s.use_nodes=True;n=s.node_tree.nodes;n.clear();links=s.node_tree.links;a=n.new('CompositorNodeRLayers');glow=n.new('CompositorNodeGlare');glow.glare_type='FOG_GLOW';glow.quality='MEDIUM';glow.threshold=2;glow.size=7;links.new(a.outputs['Image'],glow.inputs['Image']);c=n.new('CompositorNodeComposite');links.new(glow.outputs['Image'],c.inputs[0])
def emit(name,col,power):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*col,1);e.inputs[1].default_value=power;o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
def surf(name,col,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(*col,1);q.inputs['Metallic'].default_value=metal;q.inputs['Roughness'].default_value=.35;return m
ivory=emit('Distant stars',(.65,.78,1),2);guide=emit('Orbital trajectory',(.20,.36,.48),.75);gold=emit('Spacecraft trajectory',(1,.62,.22),1.8);cyan=emit('Inclined trajectory',(.22,.65,.9),1.4)
def ball(name,pos,r,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=r,location=pos);o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o
def curve(name,pts,mat,r=.012):
 mesh=bpy.data.curves.new(name,'CURVE');mesh.dimensions='3D';mesh.bevel_depth=r;mesh.bevel_resolution=2;sp=mesh.splines.new('POLY');sp.points.add(len(pts)-1)
 for v,co in zip(sp.points,pts):v.co=(*co,1)
 ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(mat);return ob
# Stars are actual spatial geometry, visible only as sparse distant light.
random.seed(81);verts=[];faces=[]
for j in range(550):
 v=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-1,1))).normalized()*random.uniform(65,100);r=random.uniform(.012,.04);i=len(verts);verts.extend([v+Vector((-r,0,0)),v+Vector((r,0,0)),v+Vector((0,r,r))]);faces.append((i,i+1,i+2))
me=bpy.data.meshes.new('Sparse distant stars');me.from_pydata(verts,[],faces);ob=bpy.data.objects.new('Sparse distant stars',me);bpy.context.collection.objects.link(ob);ob.data.materials.append(ivory)
# The solar surface has granulation and a restrained luminous corona.
m=bpy.data.materials.new('Photospheric granulation');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=34;noise.inputs['Detail'].default_value=5;r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.6,.12,.018,1);r.color_ramp.elements[1].color=(1,.8,.39,1);l.new(noise.outputs['Fac'],r.inputs[0]);e=n.new('ShaderNodeEmission');e.inputs[1].default_value=2.4;l.new(r.outputs[0],e.inputs[0]);o=n.new('ShaderNodeOutputMaterial');l.new(e.outputs[0],o.inputs[0]);sun=ball('Sun',(0,0,0),.72,m)
ld=bpy.data.lights.new('Solar illumination','POINT');ld.energy=2200;ld.use_shadow=False;ld.color=(1,.88,.72);lo=bpy.data.objects.new('Solar illumination',ld);bpy.context.collection.objects.link(lo)
earthmat=surf('Earth blue marble',(.2,.4,.7));nt=earthmat.node_tree;im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(earthfile));nt.links.new(im.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
earth=ball('Earth',(5,0,0),.33,earthmat);earth.rotation_euler=(math.radians(23.4),0,0)
# Soft blue limb; no text or diagram panel.
at=bpy.data.materials.new('Thin blue atmosphere');at.use_nodes=True;n=at.node_tree.nodes;n.clear();l=at.node_tree.links;lw=n.new('ShaderNodeLayerWeight');lw.inputs['Blend'].default_value=.2;tr=n.new('ShaderNodeBsdfTransparent');em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(.06,.3,.9,1);em.inputs[1].default_value=.65;mx=n.new('ShaderNodeMixShader');l.new(lw.outputs['Facing'],mx.inputs[0]);l.new(tr.outputs[0],mx.inputs[1]);l.new(em.outputs[0],mx.inputs[2]);o=n.new('ShaderNodeOutputMaterial');l.new(mx.outputs[0],o.inputs[0]);
if hasattr(at,'surface_render_method'):at.surface_render_method='DITHERED'
else:at.blend_method='BLEND'
air=ball('Earth atmosphere',(5,0,0),.339,at);air.hide_render=True
curve('Earth orbit',[(5*math.cos(t*math.tau/360),5*math.sin(t*math.tau/360),0) for t in range(361)],guide,.009)
for rad in [2.2,3.35,7.3]:curve('Other planetary orbit',[(rad*math.cos(t*math.tau/360),rad*math.sin(t*math.tau/360),0) for t in range(361)],guide,.006)
for i,rad in enumerate([2.2,3.35,7.3]):
 mat=surf('Rocky planet',[(.38,.29,.21),(.7,.54,.36),(.5,.18,.09)][i]);ball('Planet',(rad*math.cos(i*2+1),rad*math.sin(i*2+1),0),.10+i*.025,mat)
probe=ball('Distant spacecraft marker',(5,0,0),.055,surf('Metallic spacecraft',(.6,.65,.7),.8));probe.hide_render=True
if mode in ['turn','polar']:
 inc=math.radians(80 if mode=='polar' else 35);pts=[]
 for j in range(361):
  t=j*math.tau/360;pts.append((5*math.cos(t),5*math.sin(t)*math.cos(inc),5*math.sin(t)*math.sin(inc)))
 curve('Inclined orbit',pts,cyan,.014)
if mode=='planes':
 # Two actual spatial rings illustrate reference-plane inclination, with no claim of physical scale.
 for j in range(3):
  rad=9+j*.5;inc=math.radians(60);curve('Galactic reference plane',[(rad*math.cos(t*math.tau/360),rad*math.sin(t*math.tau/360)*math.cos(inc),rad*math.sin(t*math.tau/360)*math.sin(inc)) for t in range(361)],gold,.009)
if mode=='ulysses':
 for obj in list(s.objects):
  if obj.type in ['MESH','CURVE'] and obj.name not in ['Sun','Sparse distant stars']:obj.hide_render=True
 sun.location=(-10,6,-1);sun.scale=(.12,)*3;lo.location=sun.location
 modelpath=R/'models/Ulysses-plain.glb'
 if not modelpath.exists():
  with urllib.request.urlopen('https://assets.science.nasa.gov/content/dam/science/cds/3d/resources/model/ulysses/Ulysses.glb',timeout=90) as response:modelpath.parent.mkdir(exist_ok=True);modelpath.write_bytes(response.read())
 before=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(modelpath));objects=[o for o in s.objects if o not in before];meshobjects=[o for o in objects if o.type=='MESH'];bounds=[o.matrix_world@Vector(c) for o in meshobjects for c in o.bound_box];low=Vector(tuple(min(v[i] for v in bounds) for i in range(3)));high=Vector(tuple(max(v[i] for v in bounds) for i in range(3)));center=Vector((0,0,0));scale=2.4
 parent=bpy.data.objects.new('Ulysses display root',None);bpy.context.collection.objects.link(parent)
 for obj in objects:
  if obj.parent not in objects:obj.parent=parent
 parent.scale=(scale,)*3;parent.location=-center*scale
 key=bpy.data.lights.new('Soft spacecraft fill','AREA');key.energy=650;key.shape='DISK';key.size=6;ko=bpy.data.objects.new('Soft spacecraft fill',key);bpy.context.collection.objects.link(ko);ko.location=(4,-6,6);ko.rotation_euler=(-ko.location).to_track_quat('-Z','Y').to_euler()
# Independent, continuous camera moves and orbital motion; no restart within a source.
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=48;cam.data.clip_end=250
for f in range(1,1001,4):
 u=(f-1)/999;theta=.35+u*1.5;earth.location=(5*math.cos(theta),5*math.sin(theta),0);air.location=earth.location;earth.rotation_euler[2]=u*2;earth.keyframe_insert('location',frame=f);earth.keyframe_insert('rotation_euler',frame=f);air.keyframe_insert('location',frame=f)
 if mode=='ulysses':
  ang=-1.1+u*.8;cam.location=(11*math.cos(ang),11*math.sin(ang),3+u);target=Vector((0,0,0))
 elif mode=='close':
  ang=theta+math.pi-.5;cam.location=(earth.location.x+3.2*math.cos(ang),earth.location.y+3.2*math.sin(ang),1.4+u*.5);target=Vector(earth.location)
 else:
  ang=-1.05+u*.65;dist=18 if mode!='planes' else 24;z={'orbit':8+u*7,'turn':5+u*7,'polar':7+u*3,'planes':9-u*3}.get(mode,9);cam.location=(dist*math.cos(ang),dist*math.sin(ang),z);target=Vector((0,0,0))
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
for obj in s.objects:
 if obj.animation_data and obj.animation_data.action:
  for fc in obj.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
if pilot:s.frame_set(320);s.render.filepath=str(R/('pilot-'+mode+'.jpg'));bpy.ops.render.render(write_still=True)
else:s.render.filepath=str(out/'frame-');bpy.ops.render.render(animation=True)
