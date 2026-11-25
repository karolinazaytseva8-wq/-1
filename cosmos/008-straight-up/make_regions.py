"""Original KOSMION spatial orbit illustrations; compressed sizes and time, not flight ephemerides."""
import bpy,math,sys,pathlib,random,json,urllib.request
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];mode=args[0] if args else 'earthday';pilot='--pilot' in args;out=R/'original3d'/mode;out.mkdir(parents=True,exist_ok=True);tex=R/'textures';tex.mkdir(exist_ok=True)
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

if mode=='earthday':
 m=surf('NASA blue marble',(.2,.4,.7));nt=m.node_tree;im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(earthfile));nt.links.new(im.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color']);nt.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.85;planet=ball('Earth',(0,0,0),3,m)
 key=bpy.data.lights.new('Sunlight','AREA');key.energy=1800;key.size=8;ko=bpy.data.objects.new('Sunlight',key);bpy.context.collection.objects.link(ko);ko.location=(5,-6,4);ko.rotation_euler=(-ko.location).to_track_quat('-Z','Y').to_euler()
 fill=bpy.data.lights.new('Earthshine fill','AREA');fill.energy=130;fill.size=10;fo=bpy.data.objects.new('Earthshine fill',fill);bpy.context.collection.objects.link(fo);fo.location=(-5,-4,2);fo.rotation_euler=(-fo.location).to_track_quat('-Z','Y').to_euler()
elif mode=='oort':
 st=emit('Distant Sun',(1,.8,.4),6);ball('Distant Sun',(4,5,-1),.08,st)
 ice=surf('Ancient ice',(.36,.46,.55));nt=ice.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=12;noise.inputs['Detail'].default_value=5;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.55;bump.inputs['Distance'].default_value=.25;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal']);nt.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8
 for i in range(110):
  v=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-1,1))).normalized()*random.uniform(7,16);rr=random.uniform(.03,.11) if i>15 else random.uniform(.18,.55);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=rr,location=v);ob=bpy.context.object;ob.name='Illustrative icy body';ob.scale=(1,random.uniform(.6,1.2),random.uniform(.6,1.4));ob.data.materials.append(ice);ob.rotation_euler=(random.random()*6,random.random()*6,random.random()*6)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5,radius=1.2,location=(-2,0,0));hero=bpy.context.object;hero.name='Foreground ancient icy body';hero.scale=(1.3,.85,1);hero.data.materials.append(ice);cloud=bpy.data.textures.new('Rugged ice relief',type='CLOUDS');cloud.noise_scale=.32;dis=hero.modifiers.new('Surface relief','DISPLACE');dis.texture=cloud;dis.strength=.3
 for face in hero.data.polygons:face.use_smooth=True
 key=bpy.data.lights.new('Illustrative reflected starlight','AREA');key.energy=2800;key.color=(.65,.78,1);key.size=12;ko=bpy.data.objects.new('Illustrative reflected starlight',key);bpy.context.collection.objects.link(ko);ko.location=(0,-12,10);ko.rotation_euler=(-ko.location).to_track_quat('-Z','Y').to_euler()
elif mode=='bubble':
 # A symbolic irregular cleared cavity, not a reconstruction of measured boundary coordinates.
 shell=emit('Diffuse shell blue',(.15,.36,.5),1.1);warmcloud=emit('Diffuse shell warm',(.62,.27,.12),.9)
 for j in range(85):
  phi=random.uniform(.0,math.pi*2);theta=random.uniform(.15,math.pi-.15);rad=7*(1+.15*math.sin(phi*3)*math.sin(theta*4));v=Vector((rad*math.sin(theta)*math.cos(phi),rad*math.sin(theta)*math.sin(phi),rad*math.cos(theta)))
  if v.y<-2:continue
  pts=[]
  for k in range(15):
   u=k/14;ph=phi+u*.22;th=theta+.06*math.sin(u*7+j);r=rad+.13*math.sin(u*12);pts.append((r*math.sin(th)*math.cos(ph),r*math.sin(th)*math.sin(ph),r*math.cos(th)))
  curve('Irregular surrounding gas filament',pts,shell if j%3 else warmcloud,random.uniform(.012,.045))
 ball('Sun inside the cavity',(.7,-.3,.2),.055,emit('Sun marker',(1,.72,.3),5))
for f in range(1,1001,4):
 u=(f-1)/999
 if mode=='earthday':planet.rotation_euler[2]=.3+u*.8;planet.keyframe_insert('rotation_euler',frame=f)
 bpy.context.scene.frame_set(f)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=50;cam.data.clip_end=250
for f in range(1,1001,4):
 u=(f-1)/999
 if mode=='earthday':cam.location=(9-u,-9+u,3+u*.3);target=Vector((0,0,0))
 elif mode=='oort':cam.location=(-5+u*1.2,-6+u,2-u*.5);target=Vector((-1.5,0,0))
 else:cam.location=(3+u*3,-17+u*2,4+u);target=Vector((0,0,0))
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
for obj in s.objects:
 if obj.animation_data and obj.animation_data.action:
  for fc in obj.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
if pilot:s.frame_set(320);s.render.filepath=str(R/('pilot-'+mode+'.jpg'));bpy.ops.render.render(write_still=True)
else:s.render.filepath=str(out/'frame-');bpy.ops.render.render(animation=True)
