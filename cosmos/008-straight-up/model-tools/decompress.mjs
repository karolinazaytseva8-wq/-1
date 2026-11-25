import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule()});
for(const name of ['Ulysses']){
 const doc=await io.read(`../models/${name}.glb`);
 for(const ext of doc.getRoot().listExtensionsUsed()) if(ext.extensionName==='KHR_draco_mesh_compression')ext.dispose();
 await io.write(`../models/${name}-plain.glb`,doc);
}
